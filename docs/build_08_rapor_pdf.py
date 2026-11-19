"""docs/08-proje-raporu-2204a.md dosyasını PDF'e çevirir (reportlab, harici araç gerekmez).

Rapordaki içerik yalnızca Markdown dosyasında yaşar; bu betik onu olduğu gibi dizer.
Desteklenen Markdown: başlıklar, paragraflar, **kalın**, *italik*, `kod`, madde ve numaralı
listeler, tablolar (hizalama satırıyla), görseller ve iki boşlukla başlayan formül satırları.

Çalıştırma (depo kökünden):
    .venv/bin/python docs/build_08_rapor_pdf.py
Çıktı: docs/08-proje-raporu-2204a.pdf
"""

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DOCS = Path(__file__).resolve().parent
KAYNAK = DOCS / "08-proje-raporu-2204a.md"
CIKTI = DOCS / "08-proje-raporu-2204a.pdf"

# DejaVu Sans, rapordaki bütün özel karakterleri (ℓ, η, ‖, ≤, ₁ …) içerir.
FONT_DIZIN = Path("/usr/share/fonts/TTF")
for ad, dosya in {
    "Govde": "DejaVuSans.ttf",
    "Govde-Kalin": "DejaVuSans-Bold.ttf",
    "Govde-Italik": "DejaVuSans-Oblique.ttf",
    "Govde-KalinItalik": "DejaVuSans-BoldOblique.ttf",
    "Kod": "DejaVuSansMono.ttf",
}.items():
    pdfmetrics.registerFont(TTFont(ad, str(FONT_DIZIN / dosya)))
pdfmetrics.registerFontFamily(
    "Govde", normal="Govde", bold="Govde-Kalin", italic="Govde-Italik", boldItalic="Govde-KalinItalik"
)

KOYU = colors.HexColor("#1F2937")
GRI = colors.HexColor("#6B7280")
CIZGI = colors.HexColor("#D1D5DB")
BASLIK_ZEMIN = colors.HexColor("#EEF2F7")

S = {
    "govde": ParagraphStyle(
        "govde",
        fontName="Govde",
        fontSize=10,
        leading=14.2,
        alignment=TA_JUSTIFY,
        textColor=KOYU,
        spaceAfter=6,
    ),
    "baslik": ParagraphStyle(
        "baslik", fontName="Govde-Kalin", fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=10
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Govde-Kalin", fontSize=12.5, leading=16, spaceBefore=12, spaceAfter=6, textColor=KOYU
    ),
    "h3": ParagraphStyle(
        "h3", fontName="Govde-Kalin", fontSize=10.8, leading=14, spaceBefore=9, spaceAfter=4, textColor=KOYU
    ),
    "formul": ParagraphStyle(
        "formul", fontName="Govde", fontSize=10, leading=14, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8
    ),
    "hucre": ParagraphStyle("hucre", fontName="Govde", fontSize=8.3, leading=10.4, textColor=KOYU),
    "hucre_baslik": ParagraphStyle("hucre_baslik", fontName="Govde-Kalin", fontSize=8.3, leading=10.4),
    "aciklama": ParagraphStyle(
        "aciklama",
        fontName="Govde-Italik",
        fontSize=8.8,
        leading=11.5,
        alignment=TA_CENTER,
        textColor=GRI,
        spaceAfter=10,
    ),
    "kaynak": ParagraphStyle(
        "kaynak",
        fontName="Govde",
        fontSize=9,
        leading=12.5,
        leftIndent=0.6 * cm,
        firstLineIndent=-0.6 * cm,
        spaceAfter=5,
        textColor=KOYU,
    ),
}

GENISLIK = A4[0] - 4 * cm


def satir_ici(metin: str) -> str:
    """Markdown satır içi biçimlerini reportlab işaretlemesine çevirir."""
    metin = metin.replace("\\*", "\x00")  # kaçışlı yıldızlar
    kodlar: list[str] = []

    def kod_sakla(m):
        kodlar.append(m.group(1))
        return f"\x01{len(kodlar) - 1}\x01"

    metin = re.sub(r"`([^`]+)`", kod_sakla, metin)
    metin = metin.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    metin = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", metin)
    metin = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", metin)
    metin = re.sub(r"(https?://[^\s<)]+)", r'<link href="\1" color="#1D4ED8">\1</link>', metin)

    def kod_geri(m):
        k = kodlar[int(m.group(1))].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<font name="Kod" size="8.8">{k}</font>'

    metin = re.sub(r"\x01(\d+)\x01", kod_geri, metin)
    return metin.replace("\x00", "*")


def tablo(satirlar: list[str]) -> Table:
    def hucreler(s):
        return [h.strip() for h in s.strip().strip("|").split("|")]

    baslik = hucreler(satirlar[0])
    hizalar = []
    for h in hucreler(satirlar[1]):
        hizalar.append(
            "CENTER" if h.startswith(":") and h.endswith(":") else "RIGHT" if h.endswith(":") else "LEFT"
        )
    govde = [hucreler(s) for s in satirlar[2:]]
    sutun = len(baslik)

    # Sütun genişliği: metin uzunluğuna göre, sınırlarla
    uzun = [max(len(r[i]) if i < len(r) else 0 for r in [baslik, *govde]) for i in range(sutun)]
    agirlik = [min(max(u, 11), 55) for u in uzun]
    genislik = [GENISLIK * a / sum(agirlik) for a in agirlik]

    def hucre_stili(i, kalin):
        temel = S["hucre_baslik"] if kalin else S["hucre"]
        hiza = {"LEFT": 0, "CENTER": 1, "RIGHT": 2}[hizalar[i] if i < len(hizalar) else "LEFT"]
        return ParagraphStyle(f"h{i}{kalin}", parent=temel, alignment=hiza)

    veri = [[Paragraph(satir_ici(h), hucre_stili(i, True)) for i, h in enumerate(baslik)]]
    for r in govde:
        r = r + [""] * (sutun - len(r))
        veri.append([Paragraph(satir_ici(h), hucre_stili(i, False)) for i, h in enumerate(r[:sutun])])

    t = Table(veri, colWidths=genislik, repeatRows=1, hAlign="CENTER")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BASLIK_ZEMIN),
                ("LINEABOVE", (0, 0), (-1, 0), 0.8, KOYU),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, KOYU),
                ("LINEBELOW", (0, -1), (-1, -1), 0.8, KOYU),
                ("LINEBELOW", (0, 1), (-1, -2), 0.25, CIZGI),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def gorsel(yol: str) -> Image | None:
    dosya = (DOCS / yol).resolve()
    if not dosya.exists():
        print(f"uyarı: görsel bulunamadı: {dosya}", file=sys.stderr)
        return None
    img = Image(str(dosya))
    oran = min(GENISLIK * 0.88 / img.imageWidth, 9.5 * cm / img.imageHeight)
    img.drawWidth, img.drawHeight = img.imageWidth * oran, img.imageHeight * oran
    return img


def liste(ogeler: list[str], numarali: bool) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(satir_ici(o), S["govde"]), leftIndent=14) for o in ogeler],
        bulletType="1" if numarali else "bullet",
        bulletFormat="%s." if numarali else None,
        bulletFontName="Govde",
        bulletFontSize=9.5,
        start="1" if numarali else "•",
        leftIndent=14,
        bulletDedent=12,
    )


def donustur(md: str) -> list:
    hikaye: list = []
    satirlar = md.splitlines()
    i = 0
    kaynakca = False
    bekleyen_baslik = None  # tablo başlığını tabloyla aynı sayfada tutmak için

    def ekle(f):
        nonlocal bekleyen_baslik
        if bekleyen_baslik is not None:
            hikaye.append(KeepTogether([bekleyen_baslik, f]))
            bekleyen_baslik = None
        else:
            hikaye.append(f)

    while i < len(satirlar):
        s = satirlar[i]
        if not s.strip():
            i += 1
            continue
        if s.startswith("# "):
            ekle(Paragraph(satir_ici(s[2:]), S["baslik"]))
        elif s.startswith("## "):
            kaynakca = s[3:].strip() == "Kaynaklar"
            ekle(Paragraph(satir_ici(s[3:]), S["h2"]))
        elif s.startswith("### "):
            ekle(Paragraph(satir_ici(s[4:]), S["h3"]))
        elif s.strip() == "---":
            ekle(HRFlowable(width="100%", thickness=0.5, color=CIZGI, spaceBefore=4, spaceAfter=8))
        elif s.startswith("|"):
            blok = []
            while i < len(satirlar) and satirlar[i].startswith("|"):
                blok.append(satirlar[i])
                i += 1
            ekle(tablo(blok))
            hikaye.append(Spacer(1, 8))
            continue
        elif m := re.match(r"!\[[^\]]*\]\(([^)]+)\)", s):
            img = gorsel(m.group(1))
            aciklama = None
            if i + 1 < len(satirlar) and satirlar[i + 1].startswith("*"):
                aciklama = Paragraph(satir_ici(satirlar[i + 1].strip().strip("*")), S["aciklama"])
                i += 1
            parcalar = [p for p in (img, aciklama) if p is not None]
            if parcalar:
                ekle(KeepTogether(parcalar))
        elif re.match(r"^- ", s):
            ogeler = []
            while i < len(satirlar) and satirlar[i].startswith("- "):
                ogeler.append(satirlar[i][2:])
                i += 1
            ekle(liste(ogeler, False))
            continue
        elif re.match(r"^\d+\. ", s):
            ogeler = []
            while i < len(satirlar) and re.match(r"^\d+\. ", satirlar[i]):
                ogeler.append(re.sub(r"^\d+\. ", "", satirlar[i]))
                i += 1
            ekle(liste(ogeler, True))
            continue
        elif s.startswith("  ") and not s.startswith("   -"):
            ekle(Paragraph(satir_ici(s.strip()), S["formul"]))
        elif re.match(r"^\*\*Tablo \d+\.\*\*", s):
            bekleyen_baslik = Paragraph(satir_ici(s), ParagraphStyle("tb", parent=S["govde"], spaceAfter=4))
        elif re.match(r"^\*\*[^*]+\*\*$", s.strip()) and "=" in s:
            ekle(Paragraph(satir_ici(s), S["formul"]))
        else:
            ekle(Paragraph(satir_ici(s), S["kaynak"] if kaynakca else S["govde"]))
        i += 1
    return hikaye


def sayfa_numarasi(canvas, doc):
    canvas.saveState()
    canvas.setFont("Govde", 8)
    canvas.setFillColor(GRI)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, str(doc.page))
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(
        str(CIKTI),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="TÜBİTAK 2204-A Proje Raporu — Merkezlenmiş Kronecker İkamesi",
        author="",
    )
    doc.build(
        donustur(KAYNAK.read_text(encoding="utf-8")), onFirstPage=sayfa_numarasi, onLaterPages=sayfa_numarasi
    )
    print(f"PDF oluşturuldu: {CIKTI}")


if __name__ == "__main__":
    main()
