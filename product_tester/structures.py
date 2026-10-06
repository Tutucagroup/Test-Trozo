"""
Estructuras de campaña: presets de testeo + estructura custom definida en el brief.

Presets (campaña / conjuntos / anuncios):
  abo_1_1_n  ABO: 1 conjunto con todos los videos (presupuesto por conjunto)
  abo_1_n_1  ABO: 1 conjunto por video (aísla cada creativo)
  cbo_1_1_n  CBO: 1 conjunto con todos los videos (presupuesto en campaña)
  cbo_1_n_1  CBO: 1 conjunto por video, Meta reparte el presupuesto
  custom     Vos definís los conjuntos en campaign.adsets
"""

import copy
import datetime as dt
from dataclasses import dataclass, field

from .config import ConfigError

PRESETS = {
    "abo_1_1_n": {"budget_level": "adset", "split": "single"},
    "abo_1_n_1": {"budget_level": "adset", "split": "per_creative"},
    "cbo_1_1_n": {"budget_level": "campaign", "split": "single"},
    "cbo_1_n_1": {"budget_level": "campaign", "split": "per_creative"},
}

DEFAULT_NAMING = {
    "campaign": "{fecha} | {producto} | TEST | {estructura}",
    "adset": "{producto} | {audiencia} | AS{adset_n}",
    "ad": "{producto} | {video}",
}


class _SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


@dataclass
class PlannedAd:
    name: str
    creative_index: int  # índice 0-based en la lista de creativos


@dataclass
class PlannedAdSet:
    name: str
    targeting: dict
    daily_budget: float = None  # en moneda de la cuenta (None en CBO)
    ads: list = field(default_factory=list)


@dataclass
class PlannedCampaign:
    name: str
    structure: str
    budget_level: str  # "campaign" (CBO) o "adset" (ABO)
    objective: str
    daily_budget: float = None  # solo CBO
    adsets: list = field(default_factory=list)


def _deep_merge(base, override):
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def base_targeting(camp):
    targeting = {
        "geo_locations": {"countries": camp.get("countries") or ["US"]},
        "age_min": camp.get("age_min", 18),
        "age_max": camp.get("age_max", 65),
        "targeting_automation": {"advantage_audience": 1 if camp.get("advantage_audience", True) else 0},
    }
    if camp.get("genders"):
        targeting["genders"] = camp["genders"]
    return targeting


def _apply_audience_rules(targeting):
    """Con Advantage+ audience, Meta toma edad máx. y género como sugerencias.
    Si el conjunto restringe edad o género, se desactiva para que se respete."""
    restricted = (targeting.get("genders") or targeting.get("age_max", 65) < 65
                  or targeting.get("age_min", 18) > 25)
    if restricted and targeting.get("targeting_automation", {}).get("advantage_audience"):
        targeting["targeting_automation"] = {"advantage_audience": 0}
    return targeting


def _select(spec, n):
    """'all' o lista de índices 1-based -> lista de índices 0-based."""
    if spec in (None, "all"):
        return list(range(n))
    idx = []
    for i in spec:
        if not 1 <= int(i) <= n:
            raise ConfigError(f"El conjunto pide el video {i}, pero hay {n} videos")
        idx.append(int(i) - 1)
    return idx


def build_plan(brief, creatives, today=None):
    camp = brief.get("campaign") or {}
    structure = camp.get("structure", "abo_1_1_n")
    if structure != "custom" and structure not in PRESETS:
        raise ConfigError(f"Estructura desconocida '{structure}'. Opciones: {', '.join(PRESETS)}, custom")

    budget = camp.get("daily_budget")
    if not budget:
        raise ConfigError("Falta campaign.daily_budget")
    if structure == "custom":
        budget_level = camp.get("budget_level", "adset")
        if budget_level not in ("adset", "campaign"):
            raise ConfigError("campaign.budget_level debe ser 'adset' (ABO) o 'campaign' (CBO)")
        adset_specs = camp.get("adsets") or []
        if not adset_specs:
            raise ConfigError("Con structure: custom tenés que definir campaign.adsets")
    else:
        preset = PRESETS[structure]
        budget_level = preset["budget_level"]
        if preset["split"] == "single":
            adset_specs = [{"audiencia": camp.get("audience_label", "Broad"), "creatives": "all"}]
        else:
            adset_specs = [{"audiencia": c.label, "creatives": [i + 1]}
                           for i, c in enumerate(creatives)]

    naming = {**DEFAULT_NAMING, **{k: v for k, v in (camp.get("naming") or {}).items() if v}}
    product_name = brief["product"]["name"]
    ctx = {
        "fecha": (today or dt.date.today()).strftime("%Y-%m-%d"),
        "producto": product_name,
        "estructura": structure.upper(),
    }

    plan = PlannedCampaign(
        name=naming["campaign"].format_map(_SafeDict(ctx)),
        structure=structure,
        budget_level=budget_level,
        objective=camp.get("objective", "OUTCOME_SALES"),
        daily_budget=float(budget) if budget_level == "campaign" else None,
    )

    targeting = base_targeting(camp)
    for n, spec in enumerate(adset_specs, start=1):
        audiencia = spec.get("audiencia") or spec.get("name") or f"Conjunto {n}"
        actx = {**ctx, "audiencia": audiencia, "adset_n": n}
        adset = PlannedAdSet(
            name=naming["adset"].format_map(_SafeDict(actx)),
            targeting=_apply_audience_rules(_deep_merge(targeting, spec.get("targeting"))),
            daily_budget=float(spec.get("daily_budget") or budget) if budget_level == "adset" else None,
        )
        for ad_n, ci in enumerate(_select(spec.get("creatives"), len(creatives)), start=1):
            adctx = {**actx, "video": creatives[ci].label, "ad_n": ad_n}
            adset.ads.append(PlannedAd(name=naming["ad"].format_map(_SafeDict(adctx)), creative_index=ci))
        if not adset.ads:
            raise ConfigError(f"El conjunto '{audiencia}' no tiene videos")
        plan.adsets.append(adset)
    return plan


def total_daily_budget(plan):
    if plan.budget_level == "campaign":
        return plan.daily_budget
    return sum(a.daily_budget for a in plan.adsets)


def render_plan(plan, creatives, currency=""):
    """Árbol legible del plan para revisar antes de lanzar."""
    cur = f" {currency}" if currency else ""
    kind = "CBO" if plan.budget_level == "campaign" else "ABO"
    lines = [f"CAMPAÑA  {plan.name}  [{plan.objective}, {kind}]"]
    if plan.daily_budget:
        lines[0] += f"  presupuesto diario: {plan.daily_budget:g}{cur}"
    for adset in plan.adsets:
        geo = ",".join(adset.targeting.get("geo_locations", {}).get("countries", []))
        line = (f"  └─ CONJUNTO  {adset.name}  [{geo}, "
                f"{adset.targeting.get('age_min')}-{adset.targeting.get('age_max')}]")
        if adset.daily_budget:
            line += f"  presupuesto diario: {adset.daily_budget:g}{cur}"
        lines.append(line)
        for ad in adset.ads:
            c = creatives[ad.creative_index]
            src = c.path or c.url
            lines.append(f"       └─ AD  {ad.name}  <- {src}")
    lines.append(f"Gasto diario total: {total_daily_budget(plan):g}{cur}")
    return "\n".join(lines)
