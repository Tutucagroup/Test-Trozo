"""
Carga de credenciales (.env / variables de entorno) y del brief YAML.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigError(Exception):
    pass


def load_dotenv(path=".env"):
    """Parser mínimo de .env (KEY=VALUE). No pisa variables ya definidas."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


@dataclass
class MetaSettings:
    access_token: str
    ad_account_id: str
    page_id: str
    pixel_id: str
    instagram_user_id: str = ""
    api_version: str = "v25.0"

    @classmethod
    def from_env(cls):
        missing = [k for k in ("META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID",
                               "META_PAGE_ID", "META_PIXEL_ID") if not os.environ.get(k)]
        if missing:
            raise ConfigError(f"Faltan variables de Meta en .env: {', '.join(missing)}")
        account = os.environ["META_AD_ACCOUNT_ID"].strip()
        if not account.startswith("act_"):
            account = f"act_{account}"
        return cls(
            access_token=os.environ["META_ACCESS_TOKEN"].strip(),
            ad_account_id=account,
            page_id=os.environ["META_PAGE_ID"].strip(),
            pixel_id=os.environ["META_PIXEL_ID"].strip(),
            instagram_user_id=os.environ.get("META_INSTAGRAM_USER_ID", "").strip(),
            api_version=os.environ.get("META_API_VERSION", "v25.0").strip() or "v25.0",
        )


@dataclass
class ShopifySettings:
    store: str
    access_token: str
    api_version: str = "2026-07"
    public_domain: str = ""

    @classmethod
    def from_env(cls):
        missing = [k for k in ("SHOPIFY_STORE", "SHOPIFY_ACCESS_TOKEN") if not os.environ.get(k)]
        if missing:
            raise ConfigError(f"Faltan variables de Shopify en .env: {', '.join(missing)}")
        store = os.environ["SHOPIFY_STORE"].strip().replace("https://", "").rstrip("/")
        return cls(
            store=store,
            access_token=os.environ["SHOPIFY_ACCESS_TOKEN"].strip(),
            api_version=os.environ.get("SHOPIFY_API_VERSION", "2026-07").strip() or "2026-07",
            public_domain=os.environ.get("SHOPIFY_PUBLIC_DOMAIN", "").strip()
                .replace("https://", "").rstrip("/"),
        )


def load_brief(path):
    """Lee el brief YAML. Las rutas relativas dentro del brief se resuelven
    respecto a la carpeta del brief."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"No existe el brief: {path}")
    brief = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return normalize_brief(brief, p.parent)


def normalize_brief(brief, base_dir):
    """Valida lo mínimo y fija la carpeta base para resolver rutas relativas."""
    if not isinstance(brief, dict):
        raise ConfigError("El brief tiene que ser un objeto")
    brief = dict(brief)
    if not (brief.get("product") or {}).get("name"):
        raise ConfigError("El brief necesita product.name")
    brief["_base_dir"] = str(Path(base_dir).resolve())
    return brief


def resolve_path(brief, value):
    if not value:
        return None
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = Path(brief.get("_base_dir", ".")) / p
    return p
