"""
Orquestación: brief -> videos -> Meta (campaña/conjuntos/anuncios) apuntando a Shopify.

Patrón de seguridad: la campaña se crea en PAUSED y los conjuntos/anuncios en ACTIVE.
Nada gasta hasta que se activa la campaña (con --activate o desde el Ads Manager).
"""

import datetime as dt
import json
import re
from pathlib import Path

from .copywriting import build_copy
from .kalodata import collect_creatives
from .media import ensure_local, file_sha1
from .structures import build_plan

DEFAULT_URL_TAGS = ("utm_source=facebook&utm_medium=paid"
                    "&utm_campaign={{campaign.name}}&utm_content={{ad.name}}")


class LaunchError(Exception):
    pass


class RunLog:
    """Guarda lo creado en runs/<fecha>_<producto>.json a medida que avanza,
    así si algo falla sabés qué quedó creado en Meta."""

    def __init__(self, runs_dir, product_name):
        slug = re.sub(r"[^a-z0-9]+", "-", product_name.lower()).strip("-")
        self.dir = Path(runs_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = self.dir / f"{stamp}_{slug}.json"
        self.data = {"started_at": dt.datetime.now().isoformat(timespec="seconds"),
                     "product": product_name, "videos": {}, "adsets": [], "ads": [],
                     "status": "running"}

    def update(self, **kw):
        self.data.update(kw)
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")


class VideoCache:
    """Evita re-subir el mismo archivo a la misma cuenta publicitaria."""

    def __init__(self, runs_dir):
        self.path = Path(runs_dir) / "video_cache.json"
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def get(self, account, sha):
        return self.data.get(f"{account}:{sha}")

    def put(self, account, sha, entry):
        self.data[f"{account}:{sha}"] = entry
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))


def resolve_destination(brief, shopify):
    """Devuelve (url, product_info|None)."""
    product = brief["product"]
    if product.get("url"):
        return product["url"], None
    handle = product.get("shopify_handle")
    if not handle:
        raise LaunchError("El brief necesita product.url o product.shopify_handle")
    if shopify is None:
        raise LaunchError("product.shopify_handle requiere credenciales de Shopify en .env")
    info = shopify.get_product(handle)
    return shopify.product_url(info), info


def prepare(brief):
    creatives = collect_creatives(brief)
    plan = build_plan(brief, creatives)
    return creatives, plan


def launch(brief, meta, shopify=None, activate=False, force=False, runs_dir="runs",
           media_dir="media", log=print):
    creatives, plan = prepare(brief)
    camp_cfg = brief.get("campaign") or {}

    url, product_info = resolve_destination(brief, shopify)
    if product_info:
        log(f"Shopify: '{product_info['title']}' [{product_info['status']}] -> {url}")
        if activate and product_info["status"] != "ACTIVE" and not force:
            raise LaunchError(
                f"El producto está en {product_info['status']} en Shopify. Publicalo antes de "
                "activar la campaña, o lanzá sin --activate (o con --force)."
            )

    run = RunLog(runs_dir, brief["product"]["name"])
    run.update(destination_url=url, structure=plan.structure)
    cache = VideoCache(runs_dir)
    account = meta.s.ad_account_id

    try:
        # 1) Videos: descargar si hace falta y subir a la biblioteca de la cuenta.
        used = sorted({ad.creative_index for a in plan.adsets for ad in a.ads})
        videos = {}
        for ci in used:
            c = creatives[ci]
            path = ensure_local(c, media_dir)
            sha = file_sha1(path)
            cached = cache.get(account, sha)
            if cached:
                log(f"Video {c.label}: ya subido ({cached['video_id']})")
                videos[ci] = cached
            else:
                log(f"Subiendo video {c.label} ({path.name})...")
                video_id = meta.upload_video(path, f"{brief['product']['name']} {c.label}")
                meta.wait_video_ready(video_id)
                entry = {"video_id": video_id, "thumbnail": meta.video_thumbnail(video_id)}
                cache.put(account, sha, entry)
                videos[ci] = entry
            run.data["videos"][c.label] = videos[ci]["video_id"]
            run.save()

        # 2) Campaña (siempre PAUSED).
        campaign_id = meta.create_campaign(plan.name, plan.objective, plan.daily_budget)
        run.update(campaign_id=campaign_id, campaign_name=plan.name)
        log(f"Campaña creada: {plan.name} ({campaign_id})")

        # 3) Creativos: uno por video (se reutiliza si el video aparece en varios conjuntos).
        creative_ids = {}
        url_tags = camp_cfg.get("url_tags", DEFAULT_URL_TAGS)
        for ci in used:
            c = creatives[ci]
            primary, headline, description = build_copy(brief, c, ci)
            creative_ids[ci] = meta.create_video_creative(
                name=f"{brief['product']['name']} | {c.label}",
                video_id=videos[ci]["video_id"],
                thumbnail_url=videos[ci]["thumbnail"],
                link=url,
                primary_text=primary,
                headline=headline,
                description=description,
                cta=camp_cfg.get("cta", "SHOP_NOW"),
                url_tags=url_tags,
            )

        # 4) Conjuntos y anuncios.
        for adset in plan.adsets:
            adset_id = meta.create_adset(
                campaign_id, adset.name, adset.targeting, adset.daily_budget,
                event=camp_cfg.get("event", "PURCHASE"),
                start_time=camp_cfg.get("start_time"),
                status="ACTIVE",
            )
            run.data["adsets"].append({"id": adset_id, "name": adset.name})
            run.save()
            log(f"  Conjunto: {adset.name} ({adset_id})")
            for ad in adset.ads:
                ad_id = meta.create_ad(adset_id, ad.name, creative_ids[ad.creative_index],
                                       status="ACTIVE")
                run.data["ads"].append({"id": ad_id, "name": ad.name, "adset_id": adset_id})
                run.save()
                log(f"    Anuncio: {ad.name} ({ad_id})")

        # 5) Activación opcional.
        if activate:
            meta.set_status(campaign_id, "ACTIVE")
            log("Campaña ACTIVADA.")
        else:
            log("Campaña creada en PAUSA. Revisala en el Ads Manager y activala cuando quieras.")
        run.update(status="active" if activate else "paused")
    except Exception as e:
        run.update(status="failed", error=str(e))
        log(f"Error: {e}\nLo creado hasta ahora quedó registrado en {run.path}")
        raise
    log(f"Registro: {run.path}")
    return run.data
