# Botón de pago roto en el checkout

## Síntoma

En lugar del botón de pagar, el checkout imprime:

```
I18n Error: The value for "general.pay_now_button_label" was not a string. Found "" instead.
```

## Causa

El archivo `locales/en.default.json` del tema publicado
(`theme-export-popularsclothes-com-theme-popular`) termina con un bloque
`shopify.checkout` donde seis claves están guardadas como string vacío. El
checkout pide el texto, recibe `""` y lanza el error en vez de renderizar el
botón.

| Clave | Dónde rompe | Valor sugerido |
|---|---|---|
| `general.pay_now_button_label` | El botón de pagar (el del error) | Pay now |
| `general.complete_purchase_button_label` | El mismo botón en otros flujos | Complete purchase |
| `order_payment_collection.pay_now` | Links de pago de facturas | Pay now |
| `shipping.duties_and_taxes_options.ddp_title` | Checkout del Reino Unido (aranceles) | Duties and taxes included |
| `tips.description` | Propinas, si se activan | restaurar por defecto |
| `payment.subscription_agreement_label_html` | Suscripciones, si se activan | restaurar por defecto |

La de aranceles importa especialmente porque la tienda vende al Reino Unido:
está latente y rompe el checkout en cuanto el comprador llegue a esa opción.

## Arreglo

**Opción A — editor de idioma (recomendada).**
Tienda online → Temas → ⋯ (junto al tema activo) → *Editar contenido
predeterminado del tema* → buscar "pay now" → completar los campos vacíos.

**Opción B — código.**
Tienda online → Temas → ⋯ → *Editar código* → `locales/en.default.json` →
reemplazar el bloque `"shopify"` del final por:

```json
  "shopify": {
    "checkout": {
      "general": {
        "complete_purchase_button_label": "Complete purchase",
        "pay_now_button_label": "Pay now"
      },
      "order_payment_collection": {
        "pay_now": "Pay now"
      }
    }
  }
```

Quitar las otras tres claves hace que Shopify use sus textos por defecto.

## Por qué no se aplicó desde acá

La herramienta bloquea toda escritura sobre el tema publicado
(`themeFilesUpsert` contra el tema con rol MAIN). Es una salvaguarda del
entorno, no un problema de permisos de la tienda.

## Nota sobre el otro tema

El tema `Populars — cabecera restaurada` (sin publicar) no tiene el bloque
`shopify.checkout`, así que no arrastra este problema. Pero es un diseño
distinto: publicarlo no es el arreglo.
