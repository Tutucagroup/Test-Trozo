"""
Cliente mínimo de Shopify Admin GraphQL.

Se usa para:
  - Buscar el producto que creaste (por handle) y obtener la URL de destino del anuncio.
  - Verificar que esté ACTIVE antes de activar los anuncios.
  - (Opcional) crear un borrador con el título/descripción del brief.
"""

import requests

PRODUCT_BY_HANDLE = """
query ProductByHandle($handle: String!) {
  productByIdentifier(identifier: {handle: $handle}) {
    id
    title
    handle
    status
    onlineStoreUrl
    onlineStorePreviewUrl
    totalInventory
    variants(first: 1) {
      nodes {
        price
      }
    }
  }
}
"""

CREATE_DRAFT = """
mutation CreateDraft($product: ProductCreateInput!) {
  productCreate(product: $product) {
    product {
      id
      handle
      status
    }
    userErrors {
      field
      message
    }
  }
}
"""

SHOP_INFO = """
query ShopInfo {
  shop {
    name
    currencyCode
    primaryDomain {
      host
    }
  }
}
"""


class ShopifyError(Exception):
    pass


class ShopifyClient:
    def __init__(self, settings, session=None):
        self.s = settings
        self.url = f"https://{settings.store}/admin/api/{settings.api_version}/graphql.json"
        self.http = session or requests.Session()
        self._domain = None

    def graphql(self, query, variables=None):
        resp = self.http.post(
            self.url,
            json={"query": query, "variables": variables or {}},
            headers={"X-Shopify-Access-Token": self.s.access_token,
                     "Content-Type": "application/json"},
            timeout=60,
        )
        if resp.status_code != 200:
            raise ShopifyError(f"Shopify HTTP {resp.status_code}: {resp.text[:300]}")
        body = resp.json()
        if body.get("errors"):
            raise ShopifyError(f"Shopify GraphQL: {body['errors']}")
        return body["data"]

    def shop_info(self):
        return self.graphql(SHOP_INFO)["shop"]

    def public_domain(self):
        if self.s.public_domain:
            return self.s.public_domain
        if self._domain is None:
            self._domain = self.shop_info()["primaryDomain"]["host"]
        return self._domain

    def get_product(self, handle):
        product = self.graphql(PRODUCT_BY_HANDLE, {"handle": handle})["productByIdentifier"]
        if not product:
            raise ShopifyError(f"No existe un producto con handle '{handle}' en {self.s.store}")
        variants = product.get("variants", {}).get("nodes") or []
        product["price"] = variants[0]["price"] if variants else None
        return product

    def product_url(self, product):
        """URL pública del producto. Si no está publicado en la tienda online,
        se arma con el dominio principal (la página dará 404 hasta que lo publiques)."""
        if product.get("onlineStoreUrl"):
            return product["onlineStoreUrl"]
        return f"https://{self.public_domain()}/products/{product['handle']}"

    def create_draft(self, title, description_html="", vendor=None, product_type=None, handle=None):
        product = {"title": title, "descriptionHtml": description_html, "status": "DRAFT"}
        if vendor:
            product["vendor"] = vendor
        if product_type:
            product["productType"] = product_type
        if handle:
            product["handle"] = handle
        result = self.graphql(CREATE_DRAFT, {"product": product})["productCreate"]
        if result["userErrors"]:
            raise ShopifyError(f"Shopify no creó el producto: {result['userErrors']}")
        return result["product"]
