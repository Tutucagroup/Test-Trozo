"""
CLI:
  python -m product_tester check                    verifica credenciales Meta + Shopify
  python -m product_tester plan  brief.yaml         muestra la estructura sin tocar nada
  python -m product_tester launch brief.yaml        crea todo en Meta (campaña en pausa)
  python -m product_tester launch brief.yaml --activate
  python -m product_tester shopify <handle>         estado y URL del producto
  python -m product_tester shopify-draft brief.yaml crea el producto como borrador
  python -m product_tester web                      interfaz web local en el navegador
"""

import argparse
import html
import sys

from .config import ConfigError, MetaSettings, ShopifySettings, load_brief, load_dotenv
from .launcher import LaunchError, launch, prepare
from .structures import render_plan

RIGHTS_WARNING = (
    "Aviso: los videos de Kalodata son de creadores de TikTok. Usalos en Meta solo si "
    "tenés permiso (o son tuyos/licenciados); los reclamos de propiedad intelectual "
    "pueden deshabilitar tu cuenta publicitaria."
)


def _shopify_or_none():
    try:
        from .shopify import ShopifyClient
        return ShopifyClient(ShopifySettings.from_env())
    except ConfigError:
        return None


def cmd_plan(args):
    brief = load_brief(args.brief)
    creatives, plan = prepare(brief)
    print(render_plan(plan, creatives))
    print("\nTextos por video:")
    from .copywriting import build_copy
    for i, c in enumerate(creatives):
        primary, headline, _ = build_copy(brief, c, i)
        preview = primary.replace("\n", " ")
        print(f"  {c.label}: [{headline}] {preview[:90]}{'…' if len(preview) > 90 else ''}")
    print(f"\n{RIGHTS_WARNING}")


def cmd_launch(args):
    from .meta_ads import MetaAdsClient
    brief = load_brief(args.brief)
    meta = MetaAdsClient(MetaSettings.from_env())
    shopify = _shopify_or_none()

    creatives, plan = prepare(brief)
    print(render_plan(plan, creatives, currency=meta.currency()))
    print(f"\n{RIGHTS_WARNING}")
    if not args.yes:
        action = "crear y ACTIVAR" if args.activate else "crear (en pausa)"
        if input(f"\n¿{action} esta campaña en {meta.s.ad_account_id}? [s/N] ").strip().lower() not in ("s", "si", "sí", "y", "yes"):
            print("Cancelado.")
            return
    launch(brief, meta, shopify, activate=args.activate, force=args.force)


def cmd_check(args):
    ok = True
    try:
        from .meta_ads import MetaAdsClient
        meta = MetaAdsClient(MetaSettings.from_env())
        acc = meta.account_info()
        print(f"Meta OK: {acc.get('name')} ({meta.s.ad_account_id}) moneda={acc.get('currency')} "
              f"estado={acc.get('account_status')}")
        page = meta.get(meta.s.page_id, fields="name")
        print(f"  Página: {page.get('name')}")
        pixel = meta.get(meta.s.pixel_id, fields="name")
        print(f"  Pixel: {pixel.get('name')}")
    except Exception as e:
        ok = False
        print(f"Meta ERROR: {e}")
    shopify = None
    try:
        from .shopify import ShopifyClient
        shopify = ShopifyClient(ShopifySettings.from_env())
        shop = shopify.shop_info()
        print(f"Shopify OK: {shop['name']} ({shop['primaryDomain']['host']}) moneda={shop['currencyCode']}")
    except ConfigError as e:
        print(f"Shopify no configurado ({e}). Podés usar product.url en el brief.")
    except Exception as e:
        ok = False
        print(f"Shopify ERROR: {e}")
    return 0 if ok else 1


def cmd_shopify(args):
    from .shopify import ShopifyClient
    client = ShopifyClient(ShopifySettings.from_env())
    p = client.get_product(args.handle)
    print(f"{p['title']}  [{p['status']}]  precio={p['price']}  stock={p['totalInventory']}")
    print(f"URL: {client.product_url(p)}")
    if p["status"] != "ACTIVE":
        print("Ojo: el producto no está ACTIVE; publicalo antes de activar la campaña.")


def cmd_shopify_draft(args):
    from .shopify import ShopifyClient
    brief = load_brief(args.brief)
    product = brief["product"]
    client = ShopifyClient(ShopifySettings.from_env())
    desc = product.get("description", "")
    desc_html = "".join(f"<p>{html.escape(line)}</p>" for line in desc.splitlines() if line.strip())
    created = client.create_draft(product["name"], desc_html, vendor=product.get("vendor"),
                                  product_type=product.get("type"),
                                  handle=product.get("shopify_handle"))
    print(f"Borrador creado: {created['id']} handle={created['handle']}")
    print("Completá precio, fotos y variantes en Shopify y publicalo.")
    if not product.get("shopify_handle"):
        print(f"Agregá 'shopify_handle: {created['handle']}' al brief.")


def cmd_web(args):
    from .web import serve
    serve(port=args.port, open_browser=not args.no_browser)


def main(argv=None):
    load_dotenv()
    parser = argparse.ArgumentParser(prog="product_tester",
                                     description="Kalodata -> Meta Ads (+ Shopify) para testear productos")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="verifica credenciales").set_defaults(func=cmd_check)

    p = sub.add_parser("plan", help="muestra la estructura sin crear nada")
    p.add_argument("brief")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("launch", help="sube videos y crea la campaña en Meta")
    p.add_argument("brief")
    p.add_argument("--activate", action="store_true", help="activa la campaña al terminar")
    p.add_argument("--force", action="store_true", help="activa aunque el producto no esté ACTIVE")
    p.add_argument("-y", "--yes", action="store_true", help="no pedir confirmación")
    p.set_defaults(func=cmd_launch)

    p = sub.add_parser("shopify", help="estado y URL de un producto por handle")
    p.add_argument("handle")
    p.set_defaults(func=cmd_shopify)

    p = sub.add_parser("shopify-draft", help="crea el producto del brief como borrador")
    p.add_argument("brief")
    p.set_defaults(func=cmd_shopify_draft)

    p = sub.add_parser("web", help="abre la interfaz web local")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true", help="no abrir el navegador")
    p.set_defaults(func=cmd_web)

    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except (ConfigError, LaunchError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # errores de API: mensaje claro sin traceback
        if type(e).__name__ in {"MetaAPIError", "ShopifyError", "MediaError"}:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        raise
