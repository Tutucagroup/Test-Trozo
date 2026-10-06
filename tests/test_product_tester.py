import datetime as dt
import tempfile
import unittest
from pathlib import Path

from product_tester.config import ConfigError, MetaSettings, load_brief
from product_tester.copywriting import build_copy, clean_caption
from product_tester.kalodata import Creative, collect_creatives, from_export, parse_metric
from product_tester.launcher import LaunchError, launch
from product_tester.meta_ads import MetaAdsClient
from product_tester.structures import build_plan, total_daily_budget

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def creatives(n):
    return [Creative(label=f"V{i + 1}", path=f"/tmp/v{i}.mp4") for i in range(n)]


def brief(structure="abo_1_1_n", **camp):
    return {"product": {"name": "Prod", "url": "https://shop.test/products/prod"},
            "campaign": {"structure": structure, "daily_budget": 10, "countries": ["AR"], **camp}}


class TestParsing(unittest.TestCase):
    def test_parse_metric(self):
        self.assertEqual(parse_metric("$1.2K"), 1200)
        self.assertEqual(parse_metric("3,4M"), 3_400_000)
        self.assertEqual(parse_metric("$21,300.50"), 21300.5)
        self.assertEqual(parse_metric("12,345"), 12345)
        self.assertEqual(parse_metric("--"), 0)
        self.assertEqual(parse_metric(None), 0)

    def test_clean_caption(self):
        self.assertEqual(clean_caption("Hola 😱 #fyp #tiktokmademebuyit @tienda https://x.co/a"), "Hola 😱")
        self.assertEqual(clean_caption("línea 1 #a\n\n línea 2"), "línea 1\nlínea 2")

    def test_export_sorted_and_top_n(self):
        result = from_export(EXAMPLES / "kalodata_export_ejemplo.csv", sort_by="revenue", top_n=2)
        self.assertEqual([c.url.rsplit("/", 1)[1] for c in result], ["v3.mp4", "v1.mp4"])
        self.assertEqual(result[0].creator, "@sofi.home")

    def test_export_missing_url_column(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.csv"
            p.write_text("Title,Revenue\na,1\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                from_export(p)

    def test_videos_dir_with_captions(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.mp4").write_bytes(b"x")
            (Path(d) / "a.txt").write_text("caption a", encoding="utf-8")
            (Path(d) / "b.mp4").write_bytes(b"y")
            b = {"product": {"name": "P"}, "kalodata": {"videos_dir": d}, "_base_dir": "."}
            result = collect_creatives(b)
            self.assertEqual([c.label for c in result], ["V1-a", "V2-b"])
            self.assertEqual(result[0].caption, "caption a")

    def test_example_brief_loads(self):
        b = load_brief(EXAMPLES / "brief_ejemplo.yaml")
        self.assertEqual(len(collect_creatives(b)), 3)


class TestStructures(unittest.TestCase):
    def test_abo_1_1_n(self):
        plan = build_plan(brief("abo_1_1_n"), creatives(3), today=dt.date(2026, 1, 2))
        self.assertEqual(plan.budget_level, "adset")
        self.assertIsNone(plan.daily_budget)
        self.assertEqual(len(plan.adsets), 1)
        self.assertEqual(len(plan.adsets[0].ads), 3)
        self.assertEqual(plan.adsets[0].daily_budget, 10)
        self.assertTrue(plan.name.startswith("2026-01-02 | Prod | TEST"))

    def test_abo_1_n_1(self):
        plan = build_plan(brief("abo_1_n_1"), creatives(3))
        self.assertEqual(len(plan.adsets), 3)
        self.assertEqual([a.ads[0].creative_index for a in plan.adsets], [0, 1, 2])
        self.assertEqual(total_daily_budget(plan), 30)

    def test_cbo(self):
        plan = build_plan(brief("cbo_1_n_1"), creatives(2))
        self.assertEqual(plan.daily_budget, 10)
        self.assertTrue(all(a.daily_budget is None for a in plan.adsets))
        self.assertEqual(total_daily_budget(plan), 10)

    def test_custom_with_targeting_override(self):
        b = brief("custom", budget_level="adset", adsets=[
            {"audiencia": "Broad", "creatives": "all"},
            {"audiencia": "Mujeres", "creatives": [2], "daily_budget": 15,
             "targeting": {"genders": [2], "age_min": 25}},
        ])
        plan = build_plan(b, creatives(2))
        broad, women = plan.adsets
        self.assertEqual(len(broad.ads), 2)
        self.assertEqual(women.daily_budget, 15)
        self.assertEqual(women.targeting["genders"], [2])
        self.assertEqual(women.targeting["age_min"], 25)
        self.assertEqual(women.targeting["geo_locations"], {"countries": ["AR"]})
        self.assertNotIn("genders", broad.targeting)

    def test_custom_bad_index(self):
        b = brief("custom", adsets=[{"creatives": [5]}])
        with self.assertRaises(ConfigError):
            build_plan(b, creatives(2))

    def test_unknown_structure(self):
        with self.assertRaises(ConfigError):
            build_plan(brief("xyz"), creatives(1))


class TestCopy(unittest.TestCase):
    def test_priority(self):
        c = Creative(label="V1", caption="Caption #fyp")
        b = {"product": {"name": "P", "description": "Desc"}}
        self.assertEqual(build_copy(b, c, 0)[0], "Caption")
        b["copy"] = {"primary_texts": ["A", "B"], "headlines": ["H1", "H2"]}
        self.assertEqual(build_copy(b, c, 1)[:2], ("B", "H2"))
        b["copy"] = {"use_kalodata_caption": False}
        self.assertEqual(build_copy(b, c, 0)[0], "Desc")


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class FakeGraph:
    """Simula la Graph API: registra los POST y devuelve ids incrementales."""

    def __init__(self, currency="ARS", fail_on=None):
        self.posts = []
        self.n = 0
        self.currency = currency
        self.fail_on = fail_on

    def get(self, url, params=None, timeout=None):
        if url.endswith("/thumbnails"):
            return FakeResponse({"data": [{"uri": "https://thumb/1.jpg", "is_preferred": True}]})
        if "fields" in (params or {}) and params["fields"] == "status":
            return FakeResponse({"status": {"video_status": "ready"}})
        return FakeResponse({"currency": self.currency, "name": "Cuenta"})

    def post(self, url, data=None, files=None, timeout=None):
        edge = url.rsplit("/", 1)[1]
        self.posts.append((edge, data))
        if self.fail_on and edge == self.fail_on:
            return FakeResponse({"error": {"code": 100, "message": "Invalid parameter",
                                           "error_user_msg": "Targeting inválido"}})
        self.n += 1
        return FakeResponse({"id": f"{edge}-{self.n}"})

    def edges(self, name):
        return [d for e, d in self.posts if e == name]


def meta_client(graph):
    s = MetaSettings(access_token="t", ad_account_id="act_1", page_id="pg", pixel_id="px")
    return MetaAdsClient(s, session=graph, sleep=lambda _: None)


class TestLaunch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        for name in ("a", "b"):
            (d / f"{name}.mp4").write_bytes(name.encode())
        self.brief = brief("abo_1_n_1")
        self.brief["videos"] = [{"path": str(d / "a.mp4"), "caption": "Hola #fyp"},
                                {"path": str(d / "b.mp4"), "caption": "Chau"}]
        self.runs = d / "runs"

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_launch_paused(self):
        graph = FakeGraph()
        result = launch(self.brief, meta_client(graph), runs_dir=self.runs, log=lambda *_: None)
        self.assertEqual(result["status"], "paused")
        self.assertEqual(len(graph.edges("advideos")), 2)
        camp = graph.edges("campaigns")[0]
        self.assertEqual(camp["status"], "PAUSED")
        self.assertEqual(camp["is_adset_budget_sharing_enabled"], "false")
        adsets = graph.edges("adsets")
        self.assertEqual(len(adsets), 2)
        self.assertEqual(adsets[0]["daily_budget"], 1000)  # 10 ARS -> centavos
        self.assertIn('"pixel_id": "px"', adsets[0]["promoted_object"])
        creative = graph.edges("adcreatives")[0]
        self.assertIn('"message": "Hola"', creative["object_story_spec"])
        self.assertIn("https://shop.test/products/prod", creative["object_story_spec"])
        self.assertEqual(len(graph.edges("ads")), 2)
        # No se activó la campaña
        self.assertFalse([e for e, d in graph.posts if e == result["campaign_id"]])

    def test_video_cache_skips_reupload(self):
        graph = FakeGraph()
        launch(self.brief, meta_client(graph), runs_dir=self.runs, log=lambda *_: None)
        graph2 = FakeGraph()
        launch(self.brief, meta_client(graph2), runs_dir=self.runs, log=lambda *_: None)
        self.assertEqual(graph2.edges("advideos"), [])

    def test_activate_and_zero_decimal_currency(self):
        graph = FakeGraph(currency="CLP")
        self.brief["campaign"]["structure"] = "cbo_1_1_n"
        result = launch(self.brief, meta_client(graph), activate=True, runs_dir=self.runs,
                        log=lambda *_: None)
        self.assertEqual(graph.edges("campaigns")[0]["daily_budget"], 10)
        self.assertEqual(graph.posts[-1], (result["campaign_id"], {"status": "ACTIVE", "access_token": "t"}))
        self.assertEqual(result["status"], "active")

    def test_failure_is_logged(self):
        graph = FakeGraph(fail_on="adsets")
        with self.assertRaises(Exception) as ctx:
            launch(self.brief, meta_client(graph), runs_dir=self.runs, log=lambda *_: None)
        self.assertIn("Targeting inválido", str(ctx.exception))
        logs = [p for p in self.runs.glob("*.json") if p.name != "video_cache.json"]
        self.assertIn('"status": "failed"', logs[0].read_text())

    def test_blocks_activation_if_shopify_draft(self):
        class FakeShopify:
            def get_product(self, handle):
                return {"title": "P", "status": "DRAFT", "handle": handle, "onlineStoreUrl": None}

            def product_url(self, p):
                return "https://shop.test/products/p"

        del self.brief["product"]["url"]
        self.brief["product"]["shopify_handle"] = "p"
        with self.assertRaises(LaunchError):
            launch(self.brief, meta_client(FakeGraph()), FakeShopify(), activate=True,
                   runs_dir=self.runs, log=lambda *_: None)


if __name__ == "__main__":
    unittest.main()
