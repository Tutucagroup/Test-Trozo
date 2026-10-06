"""
Limpieza de captions de TikTok/Kalodata para usarlos como texto de anuncio.
"""

import re

_HASHTAG = re.compile(r"(?<!\w)#[\wÀ-ɏ]+")
_MENTION = re.compile(r"(?<!\w)@[\w.]+")
_URL = re.compile(r"https?://\S+")
_SPACES = re.compile(r"[ \t]+")


def clean_caption(text):
    """Quita hashtags, menciones y links; deja emojis y saltos de línea."""
    if not text:
        return ""
    text = _URL.sub("", str(text))
    text = _HASHTAG.sub("", text)
    text = _MENTION.sub("", text)
    lines = [_SPACES.sub(" ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def build_copy(brief, creative, index):
    """Devuelve (primary_text, headline, description) para un creativo.

    Prioridad del texto principal:
      1. copy.by_video[<path o url del video>].primary_text
      2. copy.primary_texts del brief (rota por índice de creativo)
      3. caption de Kalodata limpio (si copy.use_kalodata_caption != false)
      4. product.description del brief
    """
    copy_cfg = brief.get("copy") or {}
    product = brief["product"]
    per_video = (copy_cfg.get("by_video") or {}).get(creative.source) or {}

    primary = per_video.get("primary_text", "")
    overrides = copy_cfg.get("primary_texts") or []
    if not primary and overrides:
        primary = overrides[index % len(overrides)]
    elif not primary and copy_cfg.get("use_kalodata_caption", True):
        primary = clean_caption(creative.caption)
    if not primary:
        primary = product.get("description", "") or product["name"]

    headlines = copy_cfg.get("headlines") or [product["name"]]
    headline = per_video.get("headline") or headlines[index % len(headlines)]
    description = copy_cfg.get("description", "")
    return primary.strip(), headline.strip(), description.strip()
