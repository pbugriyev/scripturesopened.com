"""Precise checks for the resources page product cards.

Visible cards must keep the existing studies, add the three approved Luke
expository sermon studies at $4.99, and leave the sermon companion commented
out. Previews are partial JPEGs only: no PDFs and no file-host links.
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

# Byte-for-byte previews copied from the approved site-preview set.
NEW_PREVIEW_SHA256 = {
    "assets/products/luke_sermon_1_1-4.jpg": "516b34e47103da8ed13bc5f6b9cd3823bbf5430ac87fa9e84909f897fe19a50a",
    "assets/products/luke_sermon_1_1-4_s1.jpg": "ca63c55e7434fa043d723099743a47d2976bf1285b40aba5246cd21d81c23125",
    "assets/products/luke_sermon_1_1-4_s2.jpg": "c9ec014c1bcf92bd61c4711fdd5dd5826c586c6193cbea0498712ba771097e72",
    "assets/products/luke_sermon_1_1-4_s3.jpg": "4e792410568770ea6949fa13389a63481355c4fa8ed3d6efa679496f8ffcc238",
    "assets/products/luke_sermon_1_5-25.jpg": "9921b5b39cb5ff25189db218d42bba4494f0f6d16eb6bab4bf51b64a45e98dbe",
    "assets/products/luke_sermon_1_5-25_s1.jpg": "12239d90cdaaa0cfc778265519d45f7b4ccedc0ce7dc26fe3106a25c0a4b4b8e",
    "assets/products/luke_sermon_1_5-25_s2.jpg": "a12d89ac9a9cee75d25f6acc9bf361a91ac81dbb14c0458aea87254782974020",
    "assets/products/luke_sermon_1_5-25_s3.jpg": "a360bc93d5d35d5f3b21954cdae9b103599ef7f28a73e2c8dc8d8e64ca283a17",
    "assets/products/luke_sermon_1_26-38.jpg": "d9c5e6184aee9221513cc9dc6ff952e9fc3cfd29d4b6042ed8085c33b03572f8",
    "assets/products/luke_sermon_1_26-38_s1.jpg": "a84d434fd6b5de6b2387720a799508291f0038bffbb652383ddf18e6c98e8aec",
    "assets/products/luke_sermon_1_26-38_s2.jpg": "eb4b78a356cacb5cac2f15844d8d0e15faa94c29e4c8c87e912953a19e0da66f",
    "assets/products/luke_sermon_1_26-38_s3.jpg": "7c82af2545078de1465391609128a467c819195b918e3c09b7f312eea01774e9",
}

UNCHANGED_SHA256 = {
    "assets/products/luke.jpg": "d556ee4628eafc9123b8ce22d41a77407fb6239f431442910d8bd22449ea4e3d",
    "assets/products/luke_s1.jpg": "406b479868f9f338544e0f00185af4d96d0effbf43e0a6637fa7c81eb2eaedcc",
    "assets/products/luke_s2.jpg": "2d2076312ed64450552e7fa0852067409f5c1da16cb45f39d9fae03dca6d2e28",
    "assets/products/luke_s3.jpg": "7a6b72be8523cd75af1163d7eae7f705cc0aaf1ca2c4d235acb7e6a5853e7043",
    "assets/products/luke_companion_1_1-4.jpg": "b4eb42573bf82fc83655e792dafe1ea03585df2c9be0c03f942475f60156be54",
    "assets/products/luke_companion_1_1-4_s1.jpg": "8522eb05246393d841356f961ca4355d8b0db28a9f5676dcb26e24df4c2bfa65",
    "assets/products/luke_companion_1_1-4_s2.jpg": "a5c9664262b6d700d45f0f2781ad805b7f5c0dca7b101d484fda88cf72c2f263",
    "assets/products/luke_companion_1_1-4_s3.jpg": "ad59f4479e86f00d1a05100cad0230f6c69947cadc53a67fd8adb9dad5e28155",
}

EXPECTED_CARDS = [
    {
        "title": "Judges Bible Study",
        "blurb": "A heart-level, gospel-centered small group study through the book of Judges.",
        "price": "$4.99",
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
        "price": "$5.99",
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
        "price": "$5.99",
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
        "price": "$4.99",
        "href": "https://www.etsy.com/listing/4603633187",
        "images": [
            ("assets/products/advent.jpg", "Advent Bible Study cover"),
            ("assets/products/advent_s1.jpg", "Advent Bible Study sample page 1"),
            ("assets/products/advent_s2.jpg", "Advent Bible Study sample page 2"),
            ("assets/products/advent_s3.jpg", "Advent Bible Study sample page 3"),
        ],
    },
    {
        "title": "Luke 1:1–4 Expository Sermon Study",
        "blurb": "A 25-page expository sermon study of the dedication to Theophilus, from the Greek text to a Christ-centered outline.",
        "price": "$4.99",
        "href": "https://www.etsy.com/listing/4610989529/luke-11-4-expository-sermon-study-pdf",
        "images": [
            (
                "assets/products/luke_sermon_1_1-4.jpg",
                "Cover of the Luke 1:1–4 Expository Sermon Study, 25-page partial preview",
            ),
            (
                "assets/products/luke_sermon_1_1-4_s1.jpg",
                "Partial preview of the Luke 1:1–4 sermon study: discourse diagrams and how to use the study",
            ),
            (
                "assets/products/luke_sermon_1_1-4_s2.jpg",
                "Partial preview of the Luke 1:1–4 sermon study: big ideas and fallen condition focus",
            ),
            (
                "assets/products/luke_sermon_1_1-4_s3.jpg",
                "Partial preview of the Luke 1:1–4 sermon study: 25-minute sermon outline",
            ),
        ],
    },
    {
        "title": "Luke 1:5–25 Expository Sermon Study",
        "blurb": "A 34-page expository sermon study on the birth of John the Baptist foretold, from the Greek text to a Christ-centered outline.",
        "price": "$4.99",
        "href": "https://www.etsy.com/listing/4610990713/luke-15-25-expository-sermon-study-pdf",
        "images": [
            (
                "assets/products/luke_sermon_1_5-25.jpg",
                "Cover of the Luke 1:5–25 Expository Sermon Study, 34-page partial preview",
            ),
            (
                "assets/products/luke_sermon_1_5-25_s1.jpg",
                "Partial preview of the Luke 1:5–25 sermon study: discourse diagrams and how to use the study",
            ),
            (
                "assets/products/luke_sermon_1_5-25_s2.jpg",
                "Partial preview of the Luke 1:5–25 sermon study: big ideas and fallen condition focus",
            ),
            (
                "assets/products/luke_sermon_1_5-25_s3.jpg",
                "Partial preview of the Luke 1:5–25 sermon study: 25-minute sermon outline",
            ),
        ],
    },
    {
        "title": "Luke 1:26–38 Expository Sermon Study",
        "blurb": "A 33-page expository sermon study on the birth of Jesus foretold, from the Greek text to a Christ-centered outline.",
        "price": "$4.99",
        "href": "https://www.etsy.com/listing/4610991435/luke-126-38-expository-sermon-study-pdf",
        "images": [
            (
                "assets/products/luke_sermon_1_26-38.jpg",
                "Cover of the Luke 1:26–38 Expository Sermon Study, 33-page partial preview",
            ),
            (
                "assets/products/luke_sermon_1_26-38_s1.jpg",
                "Partial preview of the Luke 1:26–38 sermon study: discourse diagrams and how to use the study",
            ),
            (
                "assets/products/luke_sermon_1_26-38_s2.jpg",
                "Partial preview of the Luke 1:26–38 sermon study: big ideas and fallen condition focus",
            ),
            (
                "assets/products/luke_sermon_1_26-38_s3.jpg",
                "Partial preview of the Luke 1:26–38 sermon study: 25-minute sermon outline",
            ),
        ],
    },
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


def strip_comments(html: str) -> str:
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


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
        cls.visible = strip_comments(cls.html)
        parser = ProductParser()
        parser.feed(cls.visible)
        cls.products = parser.products

    def test_visible_cards_match_existing_plus_three_sermon_studies(self) -> None:
        self.assertEqual(len(self.products), len(EXPECTED_CARDS))
        for got, expected in zip(self.products, EXPECTED_CARDS):
            self.assertEqual(got["title"], expected["title"])
            self.assertEqual(got["blurbs"], [expected["blurb"]])
            self.assertEqual(got["price"], expected["price"])
            self.assertEqual(got["href"], expected["href"])
            self.assertEqual(got["button"], "Buy on Etsy")
            self.assertEqual(got["imgs"], list(expected["images"]))
            for src, alt in got["imgs"]:
                self.assertTrue(alt.strip(), f"missing alt text for {src}")
                self.assertFalse(src.lower().endswith(".pdf"))

    def test_new_cards_are_four_ninety_nine_and_link_to_approved_listings(self) -> None:
        sermons = [card for card in self.products if "Expository Sermon Study" in card["title"]]
        self.assertEqual(
            [card["title"] for card in sermons],
            [
                "Luke 1:1–4 Expository Sermon Study",
                "Luke 1:5–25 Expository Sermon Study",
                "Luke 1:26–38 Expository Sermon Study",
            ],
        )
        self.assertEqual({card["price"] for card in sermons}, {"$4.99"})
        self.assertEqual(
            [card["href"] for card in sermons],
            [
                "https://www.etsy.com/listing/4610989529/luke-11-4-expository-sermon-study-pdf",
                "https://www.etsy.com/listing/4610990713/luke-15-25-expository-sermon-study-pdf",
                "https://www.etsy.com/listing/4610991435/luke-126-38-expository-sermon-study-pdf",
            ],
        )
        joined = " ".join(card["blurbs"][0] for card in sermons)
        self.assertIn("25-page", joined)
        self.assertIn("34-page", joined)
        self.assertIn("33-page", joined)

    def test_luke_pack_and_hidden_companion_stay_in_place(self) -> None:
        titles = [card["title"] for card in self.products]
        self.assertIn("Luke Small Group Pack", titles)
        self.assertNotIn("Luke 1:1–4 Sermon Companion", titles)
        self.assertNotIn("ETSY_URL_HERE", self.visible)
        self.assertNotIn("luke_companion_", self.visible)
        self.assertIn("PLACEHOLDER: Luke 1:1-4 Sermon Companion", self.html)
        self.assertIn('src="assets/products/luke_companion_1_1-4.jpg"', self.html)
        self.assertIn('href="ETSY_URL_HERE"', self.html)
        self.assertEqual(self.html.count("<!--"), 1)
        self.assertEqual(self.html.count("-->"), 1)

    def test_preview_files_are_the_approved_partial_jpegs(self) -> None:
        for rel, digest in NEW_PREVIEW_SHA256.items():
            path = ROOT / rel
            data = path.read_bytes()
            self.assertEqual(sha256(path), digest, rel)
            self.assertLess(len(data), 100_000, rel)
            self.assertEqual(jpeg_size(data), (600, 600), rel)
            self.assertNotIn(digest, UNCHANGED_SHA256.values())

    def test_existing_luke_pack_and_companion_bytes_are_unchanged(self) -> None:
        for rel, digest in UNCHANGED_SHA256.items():
            self.assertEqual(sha256(ROOT / rel), digest, rel)

    def test_no_pdf_or_file_host_links_anywhere_in_the_site(self) -> None:
        pdfs = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf" and ".git" not in p.parts]
        self.assertEqual(pdfs, [])
        self.assertFalse(list(ROOT.rglob("listing.md")))
        forbidden = (
            "drive.google",
            "docs.google",
            "dropbox.com",
            "googleusercontent",
            "listing.md",
        )
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            for needle in forbidden:
                self.assertNotIn(needle.lower(), text, f"{needle} in {path.relative_to(ROOT)}")
        for url in re.findall(r'(?:href|src)="([^"]+)"', self.visible):
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
        self.assertIn('src="assets/arch_small.png"', self.visible)
        self.assertIn('src="assets/arch.png"', (ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertIn('href="https://www.etsy.com/shop/ScripturesOpened"', self.visible)
        self.assertIn("Shop all on Etsy", self.visible)


if __name__ == "__main__":
    unittest.main()
