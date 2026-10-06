"""
Product Tester: Kalodata -> Meta Ads (+ Shopify) para testear productos rápido.

Flujo:
  1. Leés los videos/descripciones de un producto desde Kalodata (export CSV/XLSX
     o una carpeta con los videos descargados).
  2. Elegís la estructura de campaña (preset o custom) en un "brief" YAML.
  3. La herramienta sube los videos a tu cuenta publicitaria, arma
     campaña -> conjuntos -> anuncios y apunta al producto que creaste en Shopify.
"""

__version__ = "0.1.0"
