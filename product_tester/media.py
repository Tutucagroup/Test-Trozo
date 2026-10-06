"""
Obtención de los archivos de video para subir a Meta.

- path local: se usa tal cual.
- URL directa a un archivo de video (.mp4, CDN): se descarga con requests.
- URL de TikTok / página: se descarga con yt-dlp si está instalado.
"""

import hashlib
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests

from .kalodata import VIDEO_EXTS


class MediaError(Exception):
    pass


def _slug(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _looks_like_direct_video(url):
    return Path(urlparse(url).path).suffix.lower() in VIDEO_EXTS


def _download_direct(url, dest):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "")
        if "video" not in ctype and not _looks_like_direct_video(url):
            raise MediaError(f"La URL no devolvió un video (Content-Type: {ctype}): {url}")
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return dest


def _download_ytdlp(url, dest):
    if not shutil.which("yt-dlp"):
        raise MediaError(
            f"No puedo descargar {url}: no es un archivo de video directo y yt-dlp no está "
            "instalado. Instalá yt-dlp (pip install yt-dlp) o descargá el video desde Kalodata "
            "y usá kalodata.videos_dir."
        )
    cmd = ["yt-dlp", "-f", "mp4/best", "--no-playlist", "-o", str(dest), url]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not dest.exists():
        raise MediaError(f"yt-dlp falló para {url}: {proc.stderr.strip()[-400:]}")
    return dest


def ensure_local(creative, media_dir="media"):
    """Devuelve un Path local al video del creativo, descargándolo si hace falta."""
    if creative.path:
        p = Path(creative.path)
        if not p.exists():
            raise MediaError(f"No existe el archivo de video: {p}")
        return p
    if not creative.url:
        raise MediaError(f"El creativo {creative.label} no tiene url ni path")

    media_dir = Path(media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    dest = media_dir / f"{_slug(creative.url)}.mp4"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    if _looks_like_direct_video(creative.url):
        _download_direct(creative.url, dest)
    else:
        _download_ytdlp(creative.url, dest)
    creative.path = str(dest)
    return dest


def file_sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
