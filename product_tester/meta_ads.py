"""
Cliente mínimo de la Meta Marketing API (Graph API) para crear tests de producto.

Todo se crea en PAUSED salvo que se active explícitamente.
"""

import json
import time

import requests

# Monedas sin centavos en Meta (offset 1). El resto usa offset 100.
ZERO_DECIMAL_CURRENCIES = {"CLP", "COP", "CRC", "HUF", "ISK", "IDR", "JPY", "KRW", "PYG", "TWD", "VND"}
RETRYABLE_CODES = {1, 2, 4, 17, 32, 341, 613, 80004}


class MetaAPIError(Exception):
    def __init__(self, message, payload=None):
        super().__init__(message)
        self.payload = payload or {}


class MetaAdsClient:
    def __init__(self, settings, session=None, sleep=time.sleep):
        self.s = settings
        self.base = f"https://graph.facebook.com/{settings.api_version}"
        self.video_base = f"https://graph-video.facebook.com/{settings.api_version}"
        self.http = session or requests.Session()
        self.sleep = sleep
        self._currency = None

    # ------------------------------------------------------------------ http
    def _request(self, method, path, params=None, files=None, base=None, retries=4):
        url = f"{base or self.base}/{path.lstrip('/')}"
        data = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                for k, v in (params or {}).items() if v is not None}
        data["access_token"] = self.s.access_token
        for attempt in range(retries + 1):
            if method == "GET":
                resp = self.http.get(url, params=data, timeout=120)
            else:
                resp = self.http.post(url, data=data, files=files, timeout=600)
            try:
                body = resp.json()
            except ValueError:
                body = {"error": {"message": resp.text[:300]}}
            if "error" not in body:
                return body
            err = body["error"]
            if err.get("code") in RETRYABLE_CODES and attempt < retries:
                self.sleep(2 ** (attempt + 1))
                continue
            msg = err.get("error_user_msg") or err.get("message", "error desconocido")
            title = err.get("error_user_title")
            raise MetaAPIError(f"Meta API {path}: {title + ' - ' if title else ''}{msg}", err)
        raise MetaAPIError(f"Meta API {path}: reintentos agotados")

    def get(self, path, **params):
        return self._request("GET", path, params)

    def post(self, path, **params):
        return self._request("POST", path, params)

    # --------------------------------------------------------------- cuenta
    def account_info(self):
        return self.get(self.s.ad_account_id, fields="name,currency,account_status,timezone_name")

    def currency(self):
        if self._currency is None:
            self._currency = self.account_info().get("currency", "USD")
        return self._currency

    def to_minor_units(self, amount):
        """Presupuesto en moneda de la cuenta -> unidades que espera la API."""
        offset = 1 if self.currency() in ZERO_DECIMAL_CURRENCIES else 100
        return int(round(float(amount) * offset))

    # ---------------------------------------------------------------- video
    def upload_video(self, path, name):
        with open(path, "rb") as f:
            body = self._request(
                "POST", f"{self.s.ad_account_id}/advideos",
                params={"name": name},
                files={"source": (str(name) + ".mp4", f, "video/mp4")},
                base=self.video_base,
            )
        return body["id"]

    def wait_video_ready(self, video_id, timeout=600, interval=5):
        waited = 0
        while waited <= timeout:
            status = self.get(video_id, fields="status").get("status", {})
            state = status.get("video_status")
            if state == "ready":
                return
            if state == "error":
                raise MetaAPIError(f"Meta no pudo procesar el video {video_id}: {status}")
            self.sleep(interval)
            waited += interval
        raise MetaAPIError(f"Timeout esperando que el video {video_id} quede listo")

    def video_thumbnail(self, video_id, attempts=6):
        for _ in range(attempts):
            thumbs = self.get(f"{video_id}/thumbnails").get("data", [])
            if thumbs:
                preferred = next((t for t in thumbs if t.get("is_preferred")), thumbs[0])
                return preferred["uri"]
            self.sleep(5)
        raise MetaAPIError(f"El video {video_id} no tiene miniatura todavía")

    # ------------------------------------------------------------ entidades
    def create_campaign(self, name, objective, daily_budget=None, status="PAUSED"):
        params = {
            "name": name,
            "objective": objective,
            "status": status,
            "buying_type": "AUCTION",
            "special_ad_categories": [],
        }
        if daily_budget is not None:  # CBO
            params["daily_budget"] = self.to_minor_units(daily_budget)
            params["bid_strategy"] = "LOWEST_COST_WITHOUT_CAP"
        else:  # ABO
            params["is_adset_budget_sharing_enabled"] = "false"
        return self.post(f"{self.s.ad_account_id}/campaigns", **params)["id"]

    def create_adset(self, campaign_id, name, targeting, daily_budget=None, event="PURCHASE",
                     start_time=None, status="PAUSED"):
        params = {
            "name": name,
            "campaign_id": campaign_id,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "OFFSITE_CONVERSIONS",
            "promoted_object": {"pixel_id": self.s.pixel_id, "custom_event_type": event},
            "targeting": targeting,
            "status": status,
            "start_time": start_time,
        }
        if daily_budget is not None:  # ABO
            params["daily_budget"] = self.to_minor_units(daily_budget)
            params["bid_strategy"] = "LOWEST_COST_WITHOUT_CAP"
        return self.post(f"{self.s.ad_account_id}/adsets", **params)["id"]

    def create_video_creative(self, name, video_id, thumbnail_url, link, primary_text,
                              headline, description="", cta="SHOP_NOW", url_tags=None):
        video_data = {
            "video_id": video_id,
            "image_url": thumbnail_url,
            "message": primary_text,
            "title": headline,
            "call_to_action": {"type": cta, "value": {"link": link}},
        }
        if description:
            video_data["link_description"] = description
        story = {"page_id": self.s.page_id, "video_data": video_data}
        if self.s.instagram_user_id:
            story["instagram_user_id"] = self.s.instagram_user_id
        return self.post(f"{self.s.ad_account_id}/adcreatives", name=name,
                         object_story_spec=story, url_tags=url_tags)["id"]

    def create_ad(self, adset_id, name, creative_id, status="PAUSED"):
        return self.post(f"{self.s.ad_account_id}/ads", name=name, adset_id=adset_id,
                         creative={"creative_id": creative_id}, status=status)["id"]

    def set_status(self, object_id, status):
        return self.post(object_id, status=status)
