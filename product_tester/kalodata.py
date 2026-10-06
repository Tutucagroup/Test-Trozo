"""
Fuente de creativos desde Kalodata.

Kalodata no tiene API pública, así que se soportan tres entradas (combinables):
  - kalodata.export_file: CSV/XLSX exportado desde la pestaña de Videos de un
    producto en Kalodata. Se rankea por la métrica que elijas y se toman los top N.
  - kalodata.videos_dir: carpeta con los .mp4 descargados desde Kalodata. Si hay
    un .txt con el mismo nombre, se usa como caption.
  - videos: lista manual en el brief (url o path + caption).
"""

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import ConfigError, resolve_path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}

# Nombres de columna habituales (en inglés y español). Se pueden pisar con
# kalodata.columns en el brief si tu export viene distinto.
DEFAULT_COLUMNS = {
    "url": ["video link", "video url", "tiktok link", "link", "url", "enlace del video", "enlace"],
    "caption": ["video description", "description", "video title", "title", "caption",
                "descripción", "descripcion", "título del video", "titulo"],
    "creator": ["creator", "creator name", "influencer", "creador", "nickname"],
    "revenue": ["revenue", "video revenue", "gmv", "ingresos", "ventas ($)"],
    "views": ["views", "video views", "plays", "vistas", "reproducciones"],
    "sales": ["sales", "items sold", "units sold", "ventas", "unidades vendidas"],
}


@dataclass
class Creative:
    """Un video candidato a anuncio."""
    label: str
    caption: str = ""
    url: str = ""
    path: str = ""
    creator: str = ""
    metrics: dict = field(default_factory=dict)

    @property
    def source(self):
        """Identificador estable del video (path local o URL)."""
        return self.path or self.url


def parse_metric(value):
    """'$1.2K' -> 1200.0, '3,4M' -> 3400000.0, '12,345.6' -> 12345.6, '' -> 0."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace("$", "").replace("€", "").replace(" ", "")
    if not s or s in {"-", "--"}:
        return 0.0
    mult = 1.0
    suffix = s[-1].upper()
    if suffix in "KMB":
        mult = {"K": 1e3, "M": 1e6, "B": 1e9}[suffix]
        s = s[:-1]
    # Decide si la coma es decimal ("3,4") o de miles ("12,345").
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        s = s.replace(",", "") if len(parts[-1]) == 3 else s.replace(",", ".")
    s = re.sub(r"[^0-9.\-]", "", s)
    try:
        return float(s) * mult
    except ValueError:
        return 0.0


def _read_rows(path):
    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xlsm"}:
        try:
            import openpyxl
        except ImportError as e:
            raise ConfigError("Para leer .xlsx instalá openpyxl (pip install openpyxl)") from e
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [str(h or "").strip() for h in rows[0]]
        return [dict(zip(headers, r)) for r in rows[1:] if any(c is not None for c in r)]
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(f, dialect=dialect))


def _find_column(headers, candidates):
    lower = {h.lower().strip(): h for h in headers if h}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def from_export(path, columns=None, sort_by="revenue", top_n=5, exclude=()):
    rows = _read_rows(path)
    if not rows:
        return []
    headers = list(rows[0].keys())
    mapping = {}
    for key, defaults in DEFAULT_COLUMNS.items():
        override = (columns or {}).get(key)
        mapping[key] = override if override in headers else _find_column(headers, defaults)
    if not mapping["url"]:
        raise ConfigError(
            f"No encontré la columna del link del video en {path}. "
            f"Columnas disponibles: {headers}. Indicala con kalodata.columns.url en el brief."
        )

    creatives = []
    for row in rows:
        url = str(row.get(mapping["url"]) or "").strip()
        if not url or url in exclude:
            continue
        metrics = {k: parse_metric(row.get(mapping[k])) for k in ("revenue", "views", "sales")
                   if mapping[k]}
        creatives.append(Creative(
            label="",
            url=url,
            caption=str(row.get(mapping["caption"]) or "") if mapping["caption"] else "",
            creator=str(row.get(mapping["creator"]) or "") if mapping["creator"] else "",
            metrics=metrics,
        ))

    if sort_by and any(sort_by in c.metrics for c in creatives):
        creatives.sort(key=lambda c: c.metrics.get(sort_by, 0.0), reverse=True)
    return creatives[:top_n] if top_n else creatives


def from_directory(path, exclude=()):
    path = Path(path)
    if not path.is_dir():
        raise ConfigError(f"No existe la carpeta de videos: {path}")
    creatives = []
    for video in sorted(p for p in path.iterdir() if p.suffix.lower() in VIDEO_EXTS):
        if str(video) in exclude:
            continue
        caption_file = video.with_suffix(".txt")
        caption = caption_file.read_text(encoding="utf-8").strip() if caption_file.exists() else ""
        creatives.append(Creative(label=video.stem, path=str(video), caption=caption))
    return creatives


def collect_creatives(brief):
    """Junta los creativos de todas las fuentes del brief, en orden:
    lista manual, carpeta, export. Asigna labels V1, V2, ...

    kalodata.exclude: lista de videos (path o URL) a descartar; en el export
    se descartan antes del top N, así se completa con el siguiente del ranking."""
    kd = brief.get("kalodata") or {}
    exclude = set(kd.get("exclude") or [])
    creatives = []
    for item in brief.get("videos") or []:
        path = resolve_path(brief, item.get("path"))
        if (str(path) if path else item.get("url", "")) in exclude:
            continue
        creatives.append(Creative(
            label=item.get("label", ""),
            url=item.get("url", ""),
            path=str(path) if path else "",
            caption=item.get("caption", ""),
        ))

    if kd.get("videos_dir"):
        creatives.extend(from_directory(resolve_path(brief, kd["videos_dir"]), exclude))
    if kd.get("export_file"):
        creatives.extend(from_export(
            resolve_path(brief, kd["export_file"]),
            columns=kd.get("columns"),
            sort_by=kd.get("sort_by", "revenue"),
            top_n=kd.get("top_n", 5),
            exclude=exclude,
        ))

    max_videos = (brief.get("test") or {}).get("max_videos")
    if max_videos:
        creatives = creatives[:max_videos]
    for i, c in enumerate(creatives, start=1):
        c.label = f"V{i}" + (f"-{c.label}" if c.label else "")
    if not creatives:
        raise ConfigError("No hay videos: configurá kalodata.export_file, kalodata.videos_dir o videos.")
    return creatives
