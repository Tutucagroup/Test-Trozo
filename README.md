# Product Tester: Kalodata → Meta Ads (+ Shopify)

Herramienta de línea de comandos para testear productos rápido: tomás los videos y descripciones
de un producto en Kalodata, elegís la estructura de campaña y se crea todo en Meta Ads apuntando
al producto que creaste en Shopify.

```
Kalodata (export / videos)  ──►  ranking top N  ──►  subida a la biblioteca de Meta
                                                        │
Shopify (tu producto)  ──►  URL + estado  ──────────────┤
                                                        ▼
                                 Campaña ► Conjuntos ► Anuncios (estructura que elijas)
```

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env    # completá tus credenciales
python -m product_tester check
```

### Credenciales

**Meta:** en Business Manager creá un *System User* con acceso a la cuenta publicitaria, la página
y el pixel, y generá un token con `ads_management`, `ads_read`, `pages_read_engagement` y
`business_management`. Completá `META_AD_ACCOUNT_ID`, `META_PAGE_ID`, `META_PIXEL_ID`
(y `META_INSTAGRAM_USER_ID` si querés que los anuncios salgan con tu perfil de IG).

**Shopify:** en *Configuración → Apps → Desarrollar apps* creá una app con los permisos
`read_products` y `write_products` y copiá el token de Admin API. Es opcional: si no lo configurás,
poné `product.url` en el brief.

## Flujo de trabajo

1. **Kalodata:** en el producto que te interesa, abrí la pestaña *Videos* y exportá a CSV/XLSX,
   o descargá los videos a una carpeta. Kalodata no tiene API pública, así que este paso es manual.
2. **Shopify (en paralelo):** creá el producto. También podés crear un borrador desde el brief con
   `python -m product_tester shopify-draft brief.yaml`.
3. **Brief:** copiá `examples/brief_ejemplo.yaml` y completá el producto, la fuente de videos,
   la estructura, el presupuesto y el país.
4. **Revisar:** `python -m product_tester plan brief.yaml` muestra el árbol de la campaña, qué
   video va en cada anuncio y los textos. No crea nada.
5. **Lanzar:** `python -m product_tester launch brief.yaml` sube los videos y crea la campaña
   **en pausa**. La revisás en el Ads Manager y la activás.
   Con `--activate` se activa sola, pero solo si el producto está `ACTIVE` en Shopify
   (`--force` saltea ese control).

## Estructuras de campaña

| `structure` | Presupuesto        | Conjuntos             | Para qué sirve                                    |
|-------------|--------------------|-----------------------|---------------------------------------------------|
| `abo_1_1_n` | por conjunto (ABO) | 1, con todos los videos | Validar el producto: Meta elige el mejor video  |
| `abo_1_n_1` | por conjunto (ABO) | 1 por video           | Testear creativos aislados, con gasto parejo      |
| `cbo_1_1_n` | campaña (CBO)      | 1, con todos los videos | Igual que 1-1-N, con presupuesto de campaña     |
| `cbo_1_n_1` | campaña (CBO)      | 1 por video           | Meta reparte el gasto hacia los mejores videos    |
| `custom`    | `budget_level`     | los que definas       | Audiencias distintas, combinaciones de videos     |

Ejemplo de estructura `custom`:

```yaml
campaign:
  structure: custom
  budget_level: adset          # adset = ABO, campaign = CBO
  daily_budget: 10
  countries: [AR]
  adsets:
    - audiencia: Broad
      creatives: all
    - audiencia: Mujeres 25-45
      creatives: [1, 3]        # posición del video en el ranking (V1, V3)
      daily_budget: 15
      targeting: {genders: [2], age_min: 25, age_max: 45}
```

Los nombres se arman con `campaign.naming`, que acepta `{fecha}`, `{producto}`, `{estructura}`,
`{audiencia}`, `{adset_n}`, `{video}` y `{ad_n}`. A los anuncios se les agregan UTMs
(`campaign.url_tags`) para medir en Shopify qué video vende.

## Fuentes de videos

- `kalodata.export_file`: CSV/XLSX de Kalodata. Se ordena por `sort_by` (`revenue`, `views` o
  `sales`) y se toman los `top_n` primeros. Las columnas se detectan solas (en inglés o español);
  si tu export usa otros nombres, indicalos en `kalodata.columns`.
- `kalodata.videos_dir`: carpeta con los `.mp4`. Si hay un `.txt` con el mismo nombre, se usa
  como texto del anuncio.
- `videos`: lista manual con `path` o `url` y `caption`.

Los links que no son un archivo de video directo (por ejemplo, de TikTok) se descargan con
`yt-dlp` si está instalado.

## Textos del anuncio

Por defecto se usa la descripción del video de Kalodata, sin hashtags, menciones ni links.
Si definís `copy.primary_texts` y `copy.headlines`, se reparten entre los videos. Si no hay
caption, se usa `product.description`.

## Seguridad y registro

- La campaña se crea siempre en pausa: no se gasta nada hasta que la activás.
- Cada lanzamiento queda registrado en `runs/<fecha>_<producto>.json` con los IDs creados.
  Si algo falla a mitad de camino, ahí ves qué quedó creado en Meta.
- Los videos ya subidos a la misma cuenta no se vuelven a subir (`runs/video_cache.json`).

> **Derechos de los videos:** los videos de Kalodata son de creadores de TikTok. Subirlos a Meta
> sin permiso puede generar reclamos de propiedad intelectual y la desactivación de la cuenta
> publicitaria. Usá videos propios, licenciados o con permiso del creador.

## Tests

```bash
python -m unittest discover -s tests
```
