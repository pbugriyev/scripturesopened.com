"""Checks for the resources page product cards.

Four original packs only: Judges, Luke, Acts, and Advent. The Luke expository
sermon studies and the commented Luke sermon companion are unpublished while
those packets are revised, so neither their cards nor their preview images
may appear anywhere the site can serve.
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

# Etsy listing ids for the withdrawn Luke sermon studies.
WITHDRAWN_LISTING_IDS = (
    "4610989529",
    "4610990713",
    "4610991435",
    "4611406665",
    "4611426808",
    "4611410373",
    "4611412571",
    "4611431830",
    "4611433106",
    "4611418001",
    "4611419309",
    "4611438882",
    "4611430379",
    "4611450638",
    "4611433847",
    "4609536948",
)

WITHDRAWN_NEEDLES = (
    "luke_sermon",
    "luke_companion",
    "Expository Sermon",
    "Sermon Companion",
    "ETSY_URL_HERE",
    "Luke 1:1–4",
    "Luke 1:1-4",
    "Luke 1:5–25",
    "Luke 1:26–38",
    "Luke 1:39–45",
    "Luke 1:46–56",
    "Luke 1:57–66",
    "Luke 1:67–75",
    "Luke 1:76–80",
    "Luke 2:1–7",
    "Luke 2:8–14",
    "Luke 2:15–21",
    "Luke 2:22",
    "Luke 2:33",
    "Luke 2:41–52",
    "Luke 3:1–20",
    "Luke 3:21–22",
    "Luke 3:23–38",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    def test_four_original_packs_in_order(self) -> None:
        self.assertEqual(len(self.products), 4)
        self.assertEqual([card["title"] for card in self.products], [pack["title"] for pack in PACKS])
        for got, expected in zip(self.products, PACKS):
            self.assertEqual(got["title"], expected["title"])
            self.assertEqual(got["blurbs"], [expected["blurb"]])
            self.assertEqual(got["href"], expected["href"])
            self.assertEqual(got["button"], "Buy on Etsy")
            self.assertEqual(got["imgs"], expected["images"])
            self.assertRegex(got["price"], PRICE_RE)
            for src, _alt in got["imgs"]:
                self.assertTrue((ROOT / src).is_file(), src)

    def test_prices_stay_editable_display_amounts(self) -> None:
        amounts = [card["price"] for card in self.products]
        self.assertEqual(len(amounts), 4)
        for amount in amounts:
            self.assertRegex(amount, PRICE_RE)

    def test_sermon_studies_and_companion_are_absent(self) -> None:
        self.assertNotIn("<!--", self.html)
        self.assertNotIn("-->", self.html)
        for path in site_text_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for needle in WITHDRAWN_NEEDLES + WITHDRAWN_LISTING_IDS:
                self.assertNotIn(needle, text, f"{needle} in {path.relative_to(ROOT)}")
        leftovers = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and ("luke_sermon" in path.name or "luke_companion" in path.name)
        ]
        self.assertEqual(leftovers, [])

    def test_original_pack_bytes_are_unchanged(self) -> None:
        products = ROOT / "assets" / "products"
        on_disk = sorted(path.name for path in products.iterdir() if path.is_file())
        self.assertEqual(on_disk, sorted(Path(rel).name for rel in UNCHANGED_SHA256))
        for rel, digest in UNCHANGED_SHA256.items():
            self.assertEqual(sha256(ROOT / rel), digest, rel)

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
