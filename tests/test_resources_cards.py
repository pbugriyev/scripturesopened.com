"""Checks for the resources page product cards.

Nineteen visible cards: the four original packs, then fifteen Luke expository
sermon studies in passage order. Previews are partial JPEGs only. Dollar
amounts are display copy: tests check that a price is present and well formed,
and do not pin the amount, so an authorized price sync can edit resources.html
without rewriting link, image, or hash assertions.
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

# Byte-for-byte partial previews. Hashes identify the approved cover and
# three sample pages; they are not full study files.
SERMON_PREVIEW_SHA256 = {
    "assets/products/luke_sermon_1_1-4.jpg": "f28257f0106878cb383abbd89b3c7d41c52274c203ba1cbe94535d6095f12787",
    "assets/products/luke_sermon_1_1-4_s1.jpg": "bbea279956759c980d9820c89451a494e6a97dedc05dd2060ae132a601cba45f",
    "assets/products/luke_sermon_1_1-4_s2.jpg": "42b85b5ae8b5dd2cfd213326ae2dd9673846f9e5ccb0708b0e1611d16e6de488",
    "assets/products/luke_sermon_1_1-4_s3.jpg": "7a4ff186aad79667a7f776c7b2acd1b05447848637fa90aa93165a3a35f601e3",
    "assets/products/luke_sermon_1_26-38.jpg": "63fd6de2e0b2c886f696cc7162b94089d102f48de925974d3089be148ecb45c9",
    "assets/products/luke_sermon_1_26-38_s1.jpg": "c9d65c8d39e570b24a2f1818c4c29d1e9af5ca5a846264b8dad062f07a813355",
    "assets/products/luke_sermon_1_26-38_s2.jpg": "3631bcdc4aa92a9b058ea8c2973b55395f937ff7ba63f7962ad2bd5fc8d93e50",
    "assets/products/luke_sermon_1_26-38_s3.jpg": "2ed65ddc0d09ac979f2f32f8dff0320d1674765d839da9955186ba4d2e5de8ba",
    "assets/products/luke_sermon_1_39-45.jpg": "b1badf47de865236423b8e81615a45465678de45cc9b092e88401dcc96b7736c",
    "assets/products/luke_sermon_1_39-45_s1.jpg": "6a388c66e3b28d146d9ca6246d285be512d4e2bbbb75fe7ee1049d8c7b3e0538",
    "assets/products/luke_sermon_1_39-45_s2.jpg": "f9eabe16faa97d0a1d2c27843535925e881bf0f5bf89bf127c2ebe2527141d28",
    "assets/products/luke_sermon_1_39-45_s3.jpg": "346f3620e3c550cee4e9e18dffa53a06cfe0026eb71186eb27494559aaf4bf17",
    "assets/products/luke_sermon_1_46-56.jpg": "b74f7588fb36b7f6ebef2fa14a4b9ddcb29ba3dcbe214417e83eba641a343faa",
    "assets/products/luke_sermon_1_46-56_s1.jpg": "e139981a902435f74ab8deca685028ba741367e03f704980dd063d5b47576143",
    "assets/products/luke_sermon_1_46-56_s2.jpg": "84dc4434bf3c2780235c5665fd3cfd454b4438384a529cf2bb787e2cf235d707",
    "assets/products/luke_sermon_1_46-56_s3.jpg": "e07c5924706e83bc40b82383f9999866fcbe8ba64e90e870fb1e8a6ce5fccf3b",
    "assets/products/luke_sermon_1_5-25.jpg": "e408a8af41f681df6bda45f9a337c52f7c46eed8ef43497b1139f3a109a75b79",
    "assets/products/luke_sermon_1_5-25_s1.jpg": "8b313bcaab4701de8baa9396cc1a9f03214ebd211c4e7684661246cfc6fb823e",
    "assets/products/luke_sermon_1_5-25_s2.jpg": "2d7d28e1b041d5ee9674f0fe1942261b1314a4ffa11077c072210dba6164504f",
    "assets/products/luke_sermon_1_5-25_s3.jpg": "29e94744835970746ea04be5524102f5ccb3313517a50463637161260253a57a",
    "assets/products/luke_sermon_1_57-66.jpg": "3d796a49ac1231e6c01560f57d808660d7a8be70cb72965cb7aa5279c7fd8aa3",
    "assets/products/luke_sermon_1_57-66_s1.jpg": "fa47bd0601a5f2f26d97f2b2de864d75f826b9eb40730bd3b1e210ceed898db5",
    "assets/products/luke_sermon_1_57-66_s2.jpg": "015e7057353ae407af752634d7dbe7dd5d0ffbc563c0316dcba8ab819d7c2f64",
    "assets/products/luke_sermon_1_57-66_s3.jpg": "9cabbd6aaede593e8f640707e78cf46db455f78df5809f8cbbed9cf60081b1d6",
    "assets/products/luke_sermon_1_67-75.jpg": "a29341cffd706d27e248752abf4d9e591089714446f6b203fc0c1173c911ed86",
    "assets/products/luke_sermon_1_67-75_s1.jpg": "59453fab00cb251fdef80c9bd927abb927aef4c32dd2c8a57ae4fc6b8ab49f50",
    "assets/products/luke_sermon_1_67-75_s2.jpg": "345857d192a078b61e028fb339cb4359cff0cc5cbde91485a359855382a6b71e",
    "assets/products/luke_sermon_1_67-75_s3.jpg": "b287fe4150c04c990a3d0984cd303e5c8ae026350498f35dc918357b3596e4eb",
    "assets/products/luke_sermon_1_76-80.jpg": "80632c61431071a19db9059860e825519b8b190de99e24e3fea8dd266ac4c4f2",
    "assets/products/luke_sermon_1_76-80_s1.jpg": "953a22cdf8e62accc54f865718b58fff16152668c05c12f56c66f776ac84a3be",
    "assets/products/luke_sermon_1_76-80_s2.jpg": "a3dd41e8656fcefb069910395dd5c5d8f06da4afba983f65eb3cbde816a819b6",
    "assets/products/luke_sermon_1_76-80_s3.jpg": "29b9a9bdde53a42564c6cc84fc92d3f21d077be405a5b0d872c450b5d1800f29",
    "assets/products/luke_sermon_2_1-7.jpg": "b84fb6b39695f2695a5d3955a5960f4a1d6bb751ab85b930080dcd4a2b519469",
    "assets/products/luke_sermon_2_1-7_s1.jpg": "9098ad699935846990a60e0cb5f6c39830efb7f0d0d481cf8ca85f610172d782",
    "assets/products/luke_sermon_2_1-7_s2.jpg": "70aeac13a5bec41ed2fc773fcfe006ffd1e620d482a5789762dfc2818d3dea2d",
    "assets/products/luke_sermon_2_1-7_s3.jpg": "c388fa62527a79bb5c7b06004fc5b1483c36682a5cc166d0ecc73e36787c70f2",
    "assets/products/luke_sermon_2_15-21.jpg": "680cbb0bb21ad1f986044ae8648bf0b3d5f88b09bf85b18c4115ffe00e0070cd",
    "assets/products/luke_sermon_2_15-21_s1.jpg": "5da1751a8b22242460d8e30a0d078c4ecf2a181d9b051494849da7fff1d9b5c1",
    "assets/products/luke_sermon_2_15-21_s2.jpg": "e308b84b8b57511a77a256d5bb6a2e8016384434b1e7171d0440a4a2d77cc0f3",
    "assets/products/luke_sermon_2_15-21_s3.jpg": "dbc17928ffcf3e70eb39650eb9e5d4d147db90a72874719b270b5761639de026",
    "assets/products/luke_sermon_2_41-52.jpg": "276eec4df9c7e35567c696ef5a889d7a8a398df0341c967a468f3c8daf530e01",
    "assets/products/luke_sermon_2_41-52_s1.jpg": "92aa0a801228e58f93dc540d9fd9e6e4fa5f7d7b16256777c33e8163989f004d",
    "assets/products/luke_sermon_2_41-52_s2.jpg": "e51b3fc1ae5a39ab1a4e972a43a1a7b06f500d326202640fc3c3434bf0cd0ee9",
    "assets/products/luke_sermon_2_41-52_s3.jpg": "0e979c8ccdf6e041b993fd95d1e62d3eee7b36dc7972a2a9945e350fa841f260",
    "assets/products/luke_sermon_2_8-14.jpg": "96f1cc0a950b97d2c68a8ac21b15cf4c72fbe7f03582baa50f4ede7f65619230",
    "assets/products/luke_sermon_2_8-14_s1.jpg": "a7e2a028f9c4e41f14c250ee7f478e83079985a79bcba593c95c7b59099dbc3b",
    "assets/products/luke_sermon_2_8-14_s2.jpg": "e91f9618c63b11cf41874a281612ff9e6e81f0e8ad0b2a22aebd194b886cff5a",
    "assets/products/luke_sermon_2_8-14_s3.jpg": "d3ed916eaf3e72831e5bac3ce8d34f0cefadd68737dd509d699fc0aee50d6dc3",
    "assets/products/luke_sermon_3_1-20.jpg": "700afda569e21365fc5a0b4e0ee92559733006da5ccefa6034f0bf8a75475784",
    "assets/products/luke_sermon_3_1-20_s1.jpg": "c66a4771af3dcdbe5acdeed514382db0a5cd7dbef172b68a73a7a2f123f7b91f",
    "assets/products/luke_sermon_3_1-20_s2.jpg": "2d5dc505bfbbee7ddfa15686660d41c88f22c08728163160ebc5a7bd3183f003",
    "assets/products/luke_sermon_3_1-20_s3.jpg": "d5aa6bb2c9ac611a454f215355d741f8a92dbfbdd238b0c42d0b3fea036e6cbd",
    "assets/products/luke_sermon_3_21-22.jpg": "22f3d0de4f8336112fe6029ac59e0f54196db86a8f70a5da2f03c6aa63e5f303",
    "assets/products/luke_sermon_3_21-22_s1.jpg": "621fb9572158a7862e74ab9e6f333b47e3648dfb612502c31da99c2080e80842",
    "assets/products/luke_sermon_3_21-22_s2.jpg": "39c2ad9c2837a57ec120e0cc6c5e8849e20e237e91286fba1f264c8f1f856983",
    "assets/products/luke_sermon_3_21-22_s3.jpg": "dddc1edb1c5d3a5fa8020c8e6c060a1b2ba6905ea0d63b5aa350717d25a9f9e7",
    "assets/products/luke_sermon_3_23-38.jpg": "14a86c7cf7142cfb9d9ce59c8b5f0a718b2d1086ddb86db67a637483ac4db9bc",
    "assets/products/luke_sermon_3_23-38_s1.jpg": "126c59ad5f4e367814368126a36fabcf934c4c7cd52e7fe404b67b8e37945d16",
    "assets/products/luke_sermon_3_23-38_s2.jpg": "aa52e6438ea4648d6493fe862b382a1eda1a8f0e82babc5b21dc92e2c996e65f",
    "assets/products/luke_sermon_3_23-38_s3.jpg": "493676c0f4981b7f1a095ee57fc6098fe9d1e6c13a50f29e72ecd948b46bba03",
}

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
    "assets/products/luke_companion_1_1-4.jpg": "b4eb42573bf82fc83655e792dafe1ea03585df2c9be0c03f942475f60156be54",
    "assets/products/luke_companion_1_1-4_s1.jpg": "8522eb05246393d841356f961ca4355d8b0db28a9f5676dcb26e24df4c2bfa65",
    "assets/products/luke_companion_1_1-4_s2.jpg": "a5c9664262b6d700d45f0f2781ad805b7f5c0dca7b101d484fda88cf72c2f263",
    "assets/products/luke_companion_1_1-4_s3.jpg": "ad59f4479e86f00d1a05100cad0230f6c69947cadc53a67fd8adb9dad5e28155",
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

# Passage order. Held Luke 2:22–32 and Luke 2:33–40 are omitted on purpose.
SERMONS = [
    ("1_1-4", "Luke 1:1–4", 27, "A 27-page expository sermon study of the dedication to Theophilus, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4610989529/luke-11-4-expository-sermon-study-pdf"),
    ("1_5-25", "Luke 1:5–25", 35, "A 35-page expository sermon study on the birth of John the Baptist foretold, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4610990713/luke-15-25-expository-sermon-study-pdf"),
    ("1_26-38", "Luke 1:26–38", 35, "A 35-page expository sermon study on the birth of Jesus foretold, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4610991435/luke-126-38-expository-sermon-study-pdf"),
    ("1_39-45", "Luke 1:39–45", 32, "A 32-page expository sermon study of Mary’s visit to Elizabeth, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611406665/luke-139-45-expository-sermon-study-pdf"),
    ("1_46-56", "Luke 1:46–56", 32, "A 32-page expository sermon study of Mary’s song of praise, the Magnificat, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611426808/luke-146-56-expository-sermon-study-pdf"),
    ("1_57-66", "Luke 1:57–66", 31, "A 31-page expository sermon study on the naming of John, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611410373/luke-157-66-expository-sermon-study-pdf"),
    ("1_67-75", "Luke 1:67–75", 29, "A 29-page expository sermon study of Zechariah’s song, the God who visits and redeems, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611412571/luke-167-75-expository-sermon-study-pdf"),
    ("1_76-80", "Luke 1:76–80", 29, "A 29-page expository sermon study of the dawn from on high, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611431830/luke-176-80-expository-sermon-study-pdf"),
    ("2_1-7", "Luke 2:1–7", 30, "A 30-page expository sermon study of the birth of Jesus Christ, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611433106/luke-21-7-expository-sermon-study-pdf"),
    ("2_8-14", "Luke 2:8–14", 29, "A 29-page expository sermon study of the shepherds and the angels, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611418001/luke-28-14-expository-sermon-study-pdf"),
    ("2_15-21", "Luke 2:15–21", 31, "A 31-page expository sermon study on going to see, tell, and treasure what God has done, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611419309/luke-215-21-expository-sermon-study-pdf"),
    ("2_41-52", "Luke 2:41–52", 32, "A 32-page expository sermon study of the boy Jesus in his Father’s house, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611438882/luke-241-52-expository-sermon-study-pdf"),
    ("3_1-20", "Luke 3:1–20", 33, "A 33-page expository sermon study on preparing the way of the Lord, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611430379/luke-31-20-expository-sermon-study-pdf"),
    ("3_21-22", "Luke 3:21–22", 28, "A 28-page expository sermon study of the baptism of Jesus, the beloved Son, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611450638/luke-321-22-expository-sermon-study-pdf"),
    ("3_23-38", "Luke 3:23–38", 28, "A 28-page expository sermon study of the genealogy, Son of Adam and Son of God, from the Greek text to a Christ-centered outline.", "https://www.etsy.com/listing/4611433847/luke-323-38-expository-sermon-study-pdf"),
]


def sermon_images(ref: str, display: str, pages: int) -> list[tuple[str, str]]:
    base = f"assets/products/luke_sermon_{ref}"
    title = f"{display} Expository Sermon Study"
    return [
        (f"{base}.jpg", f"Partial title-page preview of the {pages}-page {title}"),
        (f"{base}_s1.jpg", f"Partial preview of the {display} sermon study: bracket discourse diagram"),
        (f"{base}_s2.jpg", f"Partial preview of the {display} sermon study: fallen condition focus"),
        (f"{base}_s3.jpg", f"Partial preview of the {display} sermon study: 25-minute sermon outline"),
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

    def test_nineteen_visible_products_in_order(self) -> None:
        self.assertEqual(len(self.products), 19)
        self.assertEqual(len(PACKS) + len(SERMONS), 19)
        for got, expected in zip(self.products[:4], PACKS):
            self.assertEqual(got["title"], expected["title"])
            self.assertEqual(got["blurbs"], [expected["blurb"]])
            self.assertEqual(got["href"], expected["href"])
            self.assertEqual(got["button"], "Buy on Etsy")
            self.assertEqual(got["imgs"], expected["images"])
            self.assertRegex(got["price"], PRICE_RE)
        for got, sermon in zip(self.products[4:], SERMONS):
            ref, display, pages, blurb, href = sermon
            self.assertEqual(got["title"], f"{display} Expository Sermon Study")
            self.assertEqual(got["blurbs"], [blurb])
            self.assertIn(f"{pages}-page", blurb)
            self.assertEqual(got["href"], href)
            self.assertEqual(got["button"], "Buy on Etsy")
            self.assertEqual(got["imgs"], sermon_images(ref, display, pages))
            self.assertRegex(got["price"], PRICE_RE)
            for src, alt in got["imgs"]:
                self.assertTrue(alt.strip(), src)
                self.assertFalse(src.lower().endswith(".pdf"))
                self.assertTrue((ROOT / src).is_file(), src)

    def test_prices_stay_editable_display_amounts(self) -> None:
        amounts = [card["price"] for card in self.products]
        self.assertEqual(len(amounts), 19)
        for amount in amounts:
            self.assertRegex(amount, PRICE_RE)
        # The amount itself is not pinned. A later authorized price sync should
        # be able to change resources.html without failing image or link checks.

    def test_held_luke_2_passages_are_absent(self) -> None:
        for needle in (
            "Luke 2:22",
            "Luke 2:33",
            "2:22–32",
            "2:33–40",
            "2:22-32",
            "2:33-40",
            "luke_sermon_2_22",
            "luke_sermon_2_33",
        ):
            self.assertNotIn(needle, self.html)
        products = ROOT / "assets" / "products"
        self.assertEqual(list(products.glob("luke_sermon_2_22*")), [])
        self.assertEqual(list(products.glob("luke_sermon_2_33*")), [])

    def test_luke_pack_and_hidden_companion_stay_in_place(self) -> None:
        titles = [card["title"] for card in self.products]
        self.assertEqual(titles[1], "Luke Small Group Pack")
        self.assertNotIn("Luke 1:1–4 Sermon Companion", titles)
        self.assertNotIn("ETSY_URL_HERE", self.visible)
        self.assertNotIn("luke_companion_", self.visible)
        self.assertNotIn("4609536948", self.visible)
        self.assertIn("PLACEHOLDER: Luke 1:1-4 Sermon Companion", self.html)
        self.assertIn('src="assets/products/luke_companion_1_1-4.jpg"', self.html)
        self.assertIn('href="ETSY_URL_HERE"', self.html)
        self.assertEqual(self.html.count("<!--"), 1)
        self.assertEqual(self.html.count("-->"), 1)

    def test_preview_files_are_the_approved_partial_jpegs(self) -> None:
        self.assertEqual(len(SERMON_PREVIEW_SHA256), 60)
        on_disk = sorted(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "assets" / "products").glob("luke_sermon_*.jpg")
        )
        self.assertEqual(on_disk, sorted(SERMON_PREVIEW_SHA256))
        for rel, digest in SERMON_PREVIEW_SHA256.items():
            path = ROOT / rel
            data = path.read_bytes()
            self.assertEqual(sha256(path), digest, rel)
            self.assertLess(len(data), 100_000, rel)
            self.assertEqual(jpeg_size(data), (600, 600), rel)
            self.assertNotIn(digest, UNCHANGED_SHA256.values())

    def test_original_packs_and_companion_bytes_are_unchanged(self) -> None:
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
