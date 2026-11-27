"""Checks for the resources page product cards.

Four original packs, then eight Chapter 1 and five Chapter 2 Luke sermon studies.
Chapter 3 and the sermon companion stay off the site.
Previews are small JPEGs only. YouTube videos are described as free;
printable packets are described as paid.
"""

from __future__ import annotations

import hashlib
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "resources.html"
TEXT_SUFFIXES = {".html", ".css", ".md", ".js", ".json", ".yml", ".yaml", ".txt"}
PRICE_RE = re.compile(r"^\$\d+\.\d{2}$")

UNCHANGED_SHA256 = {
    "assets/products/judges.jpg": "41b4704b6792b201b0893baf0561e85ab16e929026971bc32fd9929e03ae0652",
    "assets/products/judges_s1.jpg": "03aefb55888c65d3069864c1495fab834c6db8e9e7caaf6f73c853a112f6b178",
    "assets/products/judges_s2.jpg": "8ab414b17fb5d5720ced2aab37fd36e24fc444bcfca24eee7f9db085efa0c9e4",
    "assets/products/judges_s3.jpg": "4c447441bb00a66f2d97b5df7ae4042215be8b49f9c2ce654927f72cf9f42f20",
    "assets/products/luke.jpg": "d556ee4628eafc9123b8ce22d41a77407fb6239f431442910d8bd22449ea4e3d",
    "assets/products/luke_s1.jpg": "406b479868f9f338544e0f00185af4d96d0effbf43e0a6637fa7c81eb2eaedcc",
    "assets/products/luke_s2.jpg": "2d2076312ed64450552e7fa0852067409f5c1da16cb45f39d9fae03dca6d2e28",
    "assets/products/luke_s3.jpg": "7a6b72be8523cd75af1163d7eae7f705cc0aaf1ca2c4d235acb7e6a5853e7043",
    "assets/products/acts.jpg": "e71222e7637a9c930360e08029a4a11b1a13eae52c03b320cadd2d7336ec89ac",
    "assets/products/acts_s1.jpg": "656014c8506d8a20a27a7392cd95c46c678d317027f418907883a7e80e1e9acb",
    "assets/products/acts_s2.jpg": "a70db99f8eaa3448e35b2c413e4f06e4b1939c5582bc885a00afc9a04f06426e",
    "assets/products/acts_s3.jpg": "7f1d4f6312a12bb0a682c79094a803bab93f841f713b408f62b0f93218064fe7",
    "assets/products/advent.jpg": "cbe010f529364ace3a3c8e24e2987a9a5296d6968720b7a9b1ee2015ae57c31a",
    "assets/products/advent_s1.jpg": "56749268b62c3716bac3c204e1afee9d9a5030c9d2145bbce523a436a1c9a563",
    "assets/products/advent_s2.jpg": "c741c3f53a76589b10ff5ba6a8fd04b3deecd7f200b544b1c8c587c76a94c077",
    "assets/products/advent_s3.jpg": "f0d855a6fc79d9471ee881fe3c5c95ae28ff633f08d2554194aeae26c5f1c633",
}

PACKS = [
    {
        "title": "Judges Bible Study",
        "blurb": "A heart-level, gospel-centered small group study through the book of Judges.",
        "href": "https://www.etsy.com/listing/4591816580",
        "images": [
            ("assets/products/judges.jpg", "Judges Bible Study cover"),
            ("assets/products/judges_s1.jpg", "Judges Bible Study sample page 1"),
            ("assets/products/judges_s2.jpg", "Judges Bible Study sample page 2"),
            ("assets/products/judges_s3.jpg", "Judges Bible Study sample page 3"),
        ],
    },
    {
        "title": "Luke Small Group Pack",
        "blurb": "12 sessions through all 24 chapters of Luke, with leader’s guide and printable handouts.",
        "href": "https://www.etsy.com/listing/4598847993",
        "images": [
            ("assets/products/luke.jpg", "Luke Small Group Pack cover"),
            ("assets/products/luke_s1.jpg", "Luke Small Group Pack sample page 1"),
            ("assets/products/luke_s2.jpg", "Luke Small Group Pack sample page 2"),
            ("assets/products/luke_s3.jpg", "Luke Small Group Pack sample page 3"),
        ],
    },
    {
        "title": "Acts Small Group Pack",
        "blurb": "A 12-session small group pack through the book of Acts.",
        "href": "https://www.etsy.com/listing/4600635449/acts-bible-study-small-group-pack-12",
        "images": [
            ("assets/products/acts.jpg", "Acts Small Group Pack cover"),
            ("assets/products/acts_s1.jpg", "Acts Small Group Pack sample page 1"),
            ("assets/products/acts_s2.jpg", "Acts Small Group Pack sample page 2"),
            ("assets/products/acts_s3.jpg", "Acts Small Group Pack sample page 3"),
        ],
    },
    {
        "title": "Advent Bible Study",
        "blurb": "A printable Advent study for small groups and families.",
        "href": "https://www.etsy.com/listing/4603633187",
        "images": [
            ("assets/products/advent.jpg", "Advent Bible Study cover"),
            ("assets/products/advent_s1.jpg", "Advent Bible Study sample page 1"),
            ("assets/products/advent_s2.jpg", "Advent Bible Study sample page 2"),
            ("assets/products/advent_s3.jpg", "Advent Bible Study sample page 3"),
        ],
    },
]

# Still unpublished: Chapter 3 and the companion.
EXCLUDED_LISTING_IDS = (
    "4611430379",
    "4611450638",
    "4611433847",
    "4609536948",
)

EXCLUDED_NEEDLES = (
    "luke_companion",
    "luke_sermon_3_",
    "Sermon Companion",
    "ETSY_URL_HERE",
    "Luke 3:",
    "Helm",
    "Chapell",
    "Crossway",
    "Berean",
)

# ref, display, pages, topic, etsy url. Page counts and URLs come from the approved map.
SERMONS = [
    ("1_1-4", "Luke 1:1–4", 35, "the dedication to Theophilus", "https://www.etsy.com/listing/4610989529/luke-11-4-expository-sermon-study-pdf"),
    ("1_5-25", "Luke 1:5–25", 59, "the birth of John the Baptist foretold", "https://www.etsy.com/listing/4610990713/luke-15-25-expository-sermon-study-pdf"),
    ("1_26-38", "Luke 1:26–38", 49, "the birth of Jesus foretold", "https://www.etsy.com/listing/4610991435/luke-126-38-expository-sermon-study-pdf"),
    ("1_39-45", "Luke 1:39–45", 39, "Mary’s visit to Elizabeth", "https://www.etsy.com/listing/4611406665/luke-139-45-expository-sermon-study-pdf"),
    ("1_46-56", "Luke 1:46–56", 43, "Mary’s song of praise, the Magnificat", "https://www.etsy.com/listing/4611426808/luke-146-56-expository-sermon-study-pdf"),
    ("1_57-66", "Luke 1:57–66", 41, "the naming of John", "https://www.etsy.com/listing/4611410373/luke-157-66-expository-sermon-study-pdf"),
    ("1_67-75", "Luke 1:67–75", 38, "Zechariah’s song", "https://www.etsy.com/listing/4611412571/luke-167-75-expository-sermon-study-pdf"),
    ("1_76-80", "Luke 1:76–80", 38, "the dawn from on high", "https://www.etsy.com/listing/4611431830/luke-176-80-expository-sermon-study-pdf"),
    ("2_1-7", "Luke 2:1–7", 38, "the birth of Jesus Christ", "https://www.etsy.com/listing/4611433106/luke-21-7-expository-sermon-study-pdf"),
    ("2_8-14", "Luke 2:8–14", 38, "the shepherds and the angels", "https://www.etsy.com/listing/4611418001/luke-28-14-expository-sermon-study-pdf"),
    ("2_15-21", "Luke 2:15–21", 39, "going to see, tell, and treasure", "https://www.etsy.com/listing/4611419309/luke-215-21-expository-sermon-study-pdf"),
    ("2_22-40", "Luke 2:22–40", 48, "Jesus presented at the temple", "https://www.etsy.com/listing/4626521345/luke-222-40-expository-sermon-study-pdf"),
    ("2_41-52", "Luke 2:41–52", 46, "the boy Jesus in the temple", "https://www.etsy.com/listing/4611438882/luke-241-52-expository-sermon-study-pdf"),
]


def sermon_blurb(pages: int, topic: str) -> str:
    return (
        f"A {pages}-page expository sermon study of {topic}. "
        "It follows Luke’s flow of thought through the Greek text "
        "and gives a ready-to-use outline with application grounded in the passage."
    )


def sermon_images(ref: str, display: str, pages: int) -> list[tuple[str, str]]:
    base = f"assets/products/luke_sermon_{ref}"
    title = f"{display} Expository Sermon Study"
    return [
        (f"{base}.jpg", f"Partial title-page preview of the {pages}-page {title}"),
        (f"{base}_s1.jpg", f"Partial preview of the {display} sermon study: bracket discourse diagram"),
        (f"{base}_s2.jpg", f"Partial preview of the {display} sermon study: passage focus and application"),
        (f"{base}_s3.jpg", f"Partial preview of the {display} sermon study: sermon outline"),
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_size(data: bytes) -> tuple[int, int]:
    if data[:2] != b"\xff\xd8":
        raise AssertionError("not a JPEG")
    i = 2
    while i < len(data) - 8:
        if data[i] != 0xFF:
            i += 1
            continue
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9) or marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(data):
            break
        seglen = int.from_bytes(data[i : i + 2], "big")
        if marker in (0xC0, 0xC1, 0xC2) and i + 7 <= len(data):
            height = int.from_bytes(data[i + 3 : i + 5], "big")
            width = int.from_bytes(data[i + 5 : i + 7], "big")
            return width, height
        i += seglen
    raise AssertionError("JPEG has no size marker")


def site_text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return files


class ProductParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.products: list[dict] = []
        self._cur: dict | None = None
        self._capture: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag == "article" and "product" in attr.get("class", "").split():
            self._cur = {"imgs": [], "title": "", "blurbs": [], "price": "", "href": "", "button": ""}
            self.products.append(self._cur)
            return
        if self._cur is None:
            return
        if tag == "img":
            self._cur["imgs"].append((attr.get("src", ""), attr.get("alt", "")))
        elif tag == "h3":
            self._capture = "title"
            self._buf = []
        elif tag == "p":
            self._capture = "price" if "price" in attr.get("class", "").split() else "blurb"
            self._buf = []
        elif tag == "a" and "btn" in attr.get("class", "").split() and "alt" not in attr.get("class", "").split():
            self._cur["href"] = attr.get("href", "")
            self._capture = "button"
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            self._cur = None
            self._capture = None
            self._buf = []
            return
        if self._capture is None or self._cur is None or tag not in {"h3", "p", "a"}:
            return
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        if self._capture == "title":
            self._cur["title"] = text
        elif self._capture == "price":
            self._cur["price"] = text
        elif self._capture == "blurb":
            self._cur["blurbs"].append(text)
        elif self._capture == "button":
            self._cur["button"] = text
        self._capture = None
        self._buf = []

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buf.append(data)


class ResourcesCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = RESOURCES.read_text(encoding="utf-8")
        parser = ProductParser()
        parser.feed(cls.html)
        cls.products = parser.products

    def test_seventeen_cards_including_luke_2_41_52(self) -> None:
        self.assertEqual(len(SERMONS), 13)
        self.assertEqual(len(self.products), 17)
        self.assertEqual(len(PACKS) + len(SERMONS), 17)
        for got, expected in zip(self.products[:4], PACKS):
            self.assertEqual(got["title"], expected["title"])
            self.assertEqual(got["blurbs"], [expected["blurb"]])
            self.assertEqual(got["href"], expected["href"])
            self.assertEqual(got["button"], "Buy on Etsy")
            self.assertEqual(got["imgs"], expected["images"])
            self.assertRegex(got["price"], PRICE_RE)
        for got, sermon in zip(self.products[4:], SERMONS):
            ref, display, pages, topic, href = sermon
            self.assertEqual(got["title"], f"{display} Expository Sermon Study")
            self.assertEqual(got["blurbs"], [sermon_blurb(pages, topic)])
            self.assertEqual(got["href"], href)
            self.assertEqual(got["price"], "$4.99")
            self.assertEqual(got["button"], "Buy on Etsy")
            self.assertEqual(got["imgs"], sermon_images(ref, display, pages))
            for src, alt in got["imgs"]:
                self.assertTrue(alt.strip(), src)
                self.assertFalse(src.lower().endswith(".pdf"))
                self.assertTrue((ROOT / src).is_file(), src)

    def test_excluded_passages_and_companion_stay_off_the_site(self) -> None:
        self.assertNotIn("<!--", self.html)
        self.assertNotIn("-->", self.html)
        for path in site_text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for needle in EXCLUDED_NEEDLES + EXCLUDED_LISTING_IDS:
                self.assertNotIn(needle, text, f"{needle} in {path.relative_to(ROOT)}")
        leftovers = [
            path.name
            for path in (ROOT / "assets" / "products").glob("*")
            if "luke_companion" in path.name or "luke_sermon_2_33" in path.name or "luke_sermon_3_" in path.name
        ]
        self.assertEqual(leftovers, [])

    def test_original_pack_bytes_are_unchanged(self) -> None:
        products = ROOT / "assets" / "products"
        on_disk = sorted(path.name for path in products.iterdir() if path.is_file())
        sermon_names = sorted(f"luke_sermon_{ref}{suffix}.jpg" for ref, *_ in SERMONS for suffix in ("", "_s1", "_s2", "_s3"))
        expected = sorted([Path(rel).name for rel in UNCHANGED_SHA256] + sermon_names)
        self.assertEqual(on_disk, expected)
        self.assertEqual(len(sermon_names), 52)
        for rel, digest in UNCHANGED_SHA256.items():
            self.assertEqual(sha256(ROOT / rel), digest, rel)

    def test_sermon_previews_are_small_jpegs(self) -> None:
        for ref, *_ in SERMONS:
            for suffix in ("", "_s1", "_s2", "_s3"):
                path = ROOT / "assets" / "products" / f"luke_sermon_{ref}{suffix}.jpg"
                data = path.read_bytes()
                self.assertLess(len(data), 100_000, path.name)
                self.assertEqual(jpeg_size(data), (600, 600), path.name)
        oversized = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts and path.stat().st_size > 100_000 and path.name != "arch.png"
        ]
        self.assertEqual(oversized, [])

    def test_no_pdf_or_file_host_links_anywhere_in_the_site(self) -> None:
        pdfs = [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf" and ".git" not in path.parts]
        self.assertEqual(pdfs, [])
        self.assertFalse(list(ROOT.rglob("listing.md")))
        forbidden = (
            "drive.google",
            "docs.google",
            "dropbox.com",
            "googleusercontent",
            "listing.md",
        )
        for path in site_text_files():
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            for needle in forbidden:
                self.assertNotIn(needle.lower(), text, f"{needle} in {path.relative_to(ROOT)}")
        for url in re.findall(r'(?:href|src)="([^"]+)"', self.html):
            self.assertNotIn(".pdf", url.lower(), url)
            if url.startswith("http"):
                allowed = (
                    "https://www.etsy.com/",
                    "https://www.youtube.com/",
                    "https://buymeacoffee.com/",
                    "https://fonts.googleapis.com/",
                    "https://fonts.gstatic.com",
                )
                self.assertTrue(url.startswith(allowed), url)

    def test_packets_are_not_described_as_free(self) -> None:
        ambiguous = re.compile(
            r"\bfree\b[^.!?]{0,160}\b(?:resources|studies|packets)\b"
            r"|\b(?:resources|studies|packets)\b[^.!?]{0,160}\bfree\b",
            re.IGNORECASE,
        )
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix.lower() not in {".html", ".css", ".txt", ".xml", ".md", ".yml", ".yaml"}:
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            text = re.sub(r"</(p|h1|h2|h3|a|li|div|title|article)>", ". ", raw, flags=re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"&[a-z]+;", " ", text, flags=re.IGNORECASE)
            match = ambiguous.search(text)
            self.assertIsNone(match, f"{path.relative_to(ROOT)}: {match.group(0) if match else ''}")

    def test_sitemap_lists_live_pages_only(self) -> None:
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertEqual(
            robots,
            "User-agent: *\nAllow: /\n\nSitemap: https://scripturesopened.com/sitemap.xml\n",
        )
        xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', xml)
        locs = re.findall(r"<loc>([^<]+)</loc>", xml)
        lastmods = re.findall(r"<lastmod>([^<]+)</lastmod>", xml)
        self.assertEqual(
            locs,
            [
                "https://scripturesopened.com/",
                "https://scripturesopened.com/resources.html",
                "https://scripturesopened.com/videos.html",
                "https://scripturesopened.com/support.html",
                "https://scripturesopened.com/about.html",
            ],
        )
        self.assertEqual(
            lastmods,
            ["2026-11-25", "2026-11-26", "2026-11-25", "2026-11-25", "2026-11-25"],
        )
        self.assertNotIn("404", xml)

    def test_gold_arch_branding_and_shop_link_remain(self) -> None:
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("--gold:#B89654", css)
        self.assertIn("border-top:3px solid var(--gold)", css)
        self.assertIn("minmax(min(320px,100%),1fr)", css)
        self.assertIn("nav{display:flex;flex-wrap:wrap;max-width:100%}", css)
        self.assertIn('src="assets/arch_small.png"', self.html)
        self.assertIn('src="assets/arch.png"', (ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertIn('href="https://www.etsy.com/shop/ScripturesOpened"', self.html)
        self.assertIn("Shop all on Etsy", self.html)


if __name__ == "__main__":
    unittest.main()
