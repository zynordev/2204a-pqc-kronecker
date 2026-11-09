#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması
Kuantum Sonrası Kriptografide Merkezlenmiş Kronecker İkamesi (ML-KEM)
9. Sınıf Seviyesinde Sıfırdan Mantık, Formüller, Deneyler ve Jüri Savunma Master Kitabı
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Fontları kaydet (Türkçe karakter destekli Roboto)
pdfmetrics.registerFont(TTFont('Roboto', '/usr/share/fonts/TTF/Roboto-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-Bold', '/usr/share/fonts/TTF/Roboto-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-Italic', '/usr/share/fonts/TTF/Roboto-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-BoldItalic', '/usr/share/fonts/TTF/Roboto-BoldItalic.ttf'))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Kapak sayfasında üst ve alt bilgi çizilmez

        self.saveState()
        self.setFont("Roboto", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Üst bilgi (Header)
        self.drawString(42, 804, "TÜBİTAK 2204-A Bilgisayar | Kuantum Sonrası Kriptografi (PQC) & Kronecker Savunma Rehberi")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(42, 798, 553, 798)

        # Alt bilgi (Footer)
        page_text = f"Sayfa {self._pageNumber} / {page_count}"
        self.drawRightString(553, 28, page_text)
        self.drawString(42, 28, "Öğrenci: Halil Erdem Yanık | 9. Sınıf Seviyesinde Sıfırdan Formül ve Jüri Öğrenim Kitabı")
        self.line(42, 38, 553, 38)

        self.restoreState()

def create_master_guide_pdf(output_path):
    # Sayfa Boyutları ve Kenar Boşlukları
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=42,
        rightMargin=42,
        topMargin=46,
        bottomMargin=46
    )

    printable_width = 511  # 595.27 - 84

    # Renk Paleti (2204-C Mimarisiyle Birebir Uyumlu)
    C_BLACK = colors.HexColor("#000000")
    C_NAVY = colors.HexColor("#0F172A")
    C_BLUE = colors.HexColor("#1D4ED8")
    C_CYAN = colors.HexColor("#0284C7")
    C_DARK = colors.HexColor("#1E293B")
    C_MUTED = colors.HexColor("#475569")
    C_LIGHT_BG = colors.HexColor("#F8FAFC")
    C_ICE_BG = colors.HexColor("#F0F9FF")
    C_BORDER = colors.HexColor("#CBD5E1")
    C_WARN_BG = colors.HexColor("#FFFBEB")
    C_WARN_BORDER = colors.HexColor("#F59E0B")
    C_SUCCESS_BG = colors.HexColor("#ECFDF5")
    C_SUCCESS_BORDER = colors.HexColor("#10B981")

    styles = getSampleStyleSheet()

    # Tipografi Stilleri
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Roboto-Bold',
        fontSize=20,
        leading=25,
        textColor=C_BLACK,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=10.5,
        leading=15,
        textColor=C_BLUE,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'H1_Custom',
        parent=styles['Normal'],
        fontName='Roboto-Bold',
        fontSize=13,
        leading=17,
        textColor=C_NAVY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2_Custom',
        parent=styles['Normal'],
        fontName='Roboto-Bold',
        fontSize=10.5,
        leading=14,
        textColor=C_BLUE,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=8.6,
        leading=12.2,
        textColor=C_DARK,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=8.6,
        leading=12.2,
        textColor=C_DARK,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=3
    )

    card_text = ParagraphStyle(
        'CardText',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=8,
        leading=11,
        textColor=C_DARK
    )

    speech_style = ParagraphStyle(
        'SpeechText',
        parent=styles['Normal'],
        fontName='Roboto-Italic',
        fontSize=8.6,
        leading=12.5,
        textColor=colors.HexColor("#0C4A6E")
    )

    math_box_style = ParagraphStyle(
        'MathBoxText',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=8.3,
        leading=11.6,
        textColor=C_DARK
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Roboto-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=1
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=8,
        leading=10.5,
        textColor=C_DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Roboto-Bold',
        fontSize=8,
        leading=10.5,
        textColor=C_DARK
    )

    def make_box(content_flowables, bg_color=C_LIGHT_BG, border_color=C_BORDER, padding=6, border_width=1):
        table_data = [[content_flowables]]
        t = Table(table_data, colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), border_width, border_color),
            ('TOPPADDING', (0,0), (-1,-1), padding),
            ('BOTTOMPADDING', (0,0), (-1,-1), padding),
            ('LEFTPADDING', (0,0), (-1,-1), padding + 2),
            ('RIGHTPADDING', (0,0), (-1,-1), padding + 2),
        ]))
        return t

    def make_callout(title, text, kind="info"):
        if kind == "warn":
            bg = C_WARN_BG
            b_col = C_WARN_BORDER
            t_col = colors.HexColor("#92400E")
        elif kind == "success":
            bg = C_SUCCESS_BG
            b_col = C_SUCCESS_BORDER
            t_col = colors.HexColor("#065F46")
        else:
            bg = C_ICE_BG
            b_col = C_CYAN
            t_col = C_BLUE

        p_title = Paragraph(f"<b>{title}</b>", ParagraphStyle('CalloutT', fontName='Roboto-Bold', fontSize=8.8, leading=11.5, textColor=t_col, spaceAfter=2))
        p_text = Paragraph(text, ParagraphStyle('CalloutB', fontName='Roboto', fontSize=8.3, leading=11.5, textColor=C_DARK))
        return make_box([p_title, p_text], bg_color=bg, border_color=b_col, border_width=1.2, padding=6)

    story = []

    # =========================================================================
    # SAYFA 1: KAPAK SAYFASI & 30 SANİYELİK ASANSÖR KONUŞMASI
    # =========================================================================
    story.append(Spacer(1, 10))

    # Üst Başlık Yazıları (Tam Siyah Metin, Kenarlıksız Temiz Düzen)
    story.append(Paragraph("TÜBİTAK 2204-A LİSE ÖĞRENCİLERİ ARAŞTIRMA PROJELERİ YARIŞMASI", ParagraphStyle('TopHeader1', fontName='Roboto-Bold', fontSize=10.5, leading=14, textColor=C_BLACK, spaceAfter=2)))
    story.append(Paragraph("BİLGİSAYAR / SİBER GÜVENLİK ALANI — SIFIRDAN ÖĞRENİM VE JÜRİ SAVUNMA MASTER KİTABI", ParagraphStyle('TopHeader2', fontName='Roboto-Bold', fontSize=9, leading=12, textColor=colors.HexColor("#334155"), spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("Kuantum Sonrası Güvenli İletişimde Merkezlenmiş Kronecker İkamesi ile Polinom Çarpımı", title_style))
    story.append(Paragraph("NIST FIPS 203 ML-KEM Standardında Katsayı Optimizasyonu, H4 Güvenlik Analizi, ESP32 Donanım Doğrulaması ve Sıfırdan Öğrenim Kılavuzu", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    # 3 Sütunlu Rozet Tablosu
    badge_data = [
        [
            Paragraph("<b>Araştırmacı:</b> Halil Erdem Yanık<br/><b>Alan:</b> Bilgisayar / Siber Güvenlik<br/><b>Yarışma:</b> TÜBİTAK 2204-A Lise", card_text),
            Paragraph("<b>Kripto Standart:</b> NIST FIPS 203 (ML-KEM)<br/><b>Cebirsel Yapı:</b> R_q = Z_q[X]/(X²⁵⁶+1)<br/><b>Özgün Buluş:</b> 22-Bit Kronecker İkamesi", card_text),
            Paragraph("<b>Donanım Testi:</b> ESP32 NodeMCU (80 MHz)<br/><b>Mikro Bellek:</b> 768 Bayt Ara Tamponsuz<br/><b>Yazılım:</b> PQC-Drop Dosya Aktarımı", card_text)
        ]
    ]
    t_badges = Table(badge_data, colWidths=[165, 180, 166])
    t_badges.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_badges)
    story.append(Spacer(1, 10))

    # Öğrenciye Not
    intro_box = [
        Paragraph("<b>BU REHBERİN AMACI VE HALİL'E ÖZEL NOT:</b>", ParagraphStyle('IntroH', fontName='Roboto-Bold', fontSize=9, leading=12, textColor=C_NAVY, spaceAfter=3)),
        Paragraph("Sevgili Halil; bu kitapçık projenin içindeki tüm matematiği, formülleri, algoritmaları ve donanım testlerini bir 9. sınıf öğrencisi olarak <b>sıfırdan, hiçbir ezbere ihtiyaç duymadan, kristal netliğinde anlaman</b> için hazırlandı. Bu rehberi bitirdiğinde; kuantum bilgisayarların neden RSA'yı yıktığını, senin bulduğun 23² binom hilesinin Kronecker ile nasıl çalıştığını, 22 bitin altındaki tehlikeyi ve ESP32 çipinde 768 baytlık yerel RAM başarısını jüriye en üst düzey bilimsel özgüvenle anlatabileceksin.", body_style)
    ]
    story.append(make_box(intro_box, bg_color=C_ICE_BG, border_color=C_CYAN, padding=7))
    story.append(Spacer(1, 10))

    # 30 Saniyelik Asansör Konuşması
    story.append(Paragraph("🎯 30 Saniyelik Asansör Konuşması (Jüriye İlk Giriş Cümlen)", h2_style))
    speech_text = (
        "<i>\"Değerli jüri üyeleri; bugün bankacılık ve internette kullandığımız klasik şifreler (RSA), kuantum bilgisayarların "
        "çıkışıyla dakikalar içinde kırılabilecektir. NIST bu tehdide karşı Ağustos 2024'te resmi dünya standardı <b>ML-KEM</b>'i yayımladı. "
        "Ancak ML-KEM'in kalbinde mikrodenetleyicileri çok yoran 256 terimli dev polinom çarpımları vardır.<br/><br/>"
        "Biz bu projede, polinom katsayılarını tek bir büyük sayıya paketleyip tek vuruşta çarpan <b>Kronecker ikamesini</b> inceledik. "
        "Katsayıları sıfır etrafında merkezleyerek gereken tamsayı boyutunu <b>32 bitten 22 bite indirdik (%34 bellek tasarrufu)</b>. "
        "Bu sınırın altına inildiğinde gizli anahtarın nasıl sızdığını ispatladık. Yöntemimizi güvenli dosya aktarımı yapan <b>PQC-Drop</b> yazılımında "
        "ve fiziksel bir <b>ESP32 çipinde 768 baytlık ultra-düşük RAM tamponuyla</b> başarıyla çalıştırdık.\"</i>"
    )
    story.append(make_box([Paragraph(speech_text, speech_style)], bg_color=colors.HexColor("#F8FAFC"), border_color=C_BLUE, border_width=1.5, padding=8))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 2: BÖLÜM 1: KRİPTOGRAFİYE GİRİŞ VE KUANTUM TEHDİDİ
    # =========================================================================
    story.append(Paragraph("1. KRİPTOGRAFİNİN EN TEMEL MANTIK VE KUANTUM TEHDİDİ", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("A. Simetrik ve Asimetrik Şifreleme Ne Demektir?", h2_style))
    story.append(Paragraph(
        "• <b>Simetrik Şifreleme (Örnek: AES-256):</b> Tek bir ortak anahtar vardır. Bir sandığı aynı anahtarla kilitlersiniz, arkadaşınız da aynı anahtarla açar. "
        "Çok hızlıdır (saniyede yüzlerce megabayt kilitler). Ama dev bir problem vardır: <i>Bu anahtarı internet üzerinden karşı tarafa nasıl göndereceksiniz?</i> "
        "Yolda biri dinliyorsa anahtarı çalar ve tüm sandığı açar!<br/>"
        "• <b>Asimetrik Şifreleme (Örnek: RSA, ML-KEM):</b> İki ayrı anahtar vardır: <b>Açık Anahtar (Public Key)</b> ve <b>Gizli Anahtar (Private Key)</b>. "
        "Bunu mahalledeki posta kutusu gibi düşünün: Posta kutusunun ağzı herkese açıktır; isteyen herkes içine zarf atabilir (açık anahtarla şifreler). "
        "Fakat kutunun arkasındaki asma kilidi sadece posta sahibinin cebindeki özel anahtar açabilir (gizli anahtar).",
        body_style
    ))

    story.append(Paragraph("B. Hibrit Model ve KEM (Key Encapsulation Mechanism) Nedir?", h2_style))
    story.append(Paragraph(
        "Büyük dosyaları (örneğin 50 MB'lık bir PDF veya fotoğrafı) yavaş çalışan asimetrik şifrelemeyle şifreleyemezsiniz. Bu yüzden dünyadaki tüm modern sistemler <b>Hibrit Model</b> kullanır:<br/>"
        "1. Dosyayı ışık hızında çalışan <b>AES-256</b> kilitler.<br/>"
        "2. AES'in 256-bitlik minicik anahtarını ise <b>ML-KEM</b> güvenli bir zarfın (kapsülün) içine koyar.<br/>"
        "3. KEM işte bu küçük anahtarı kapsülleme ve kapsülden çıkarma mekanizmasıdır.",
        body_style
    ))

    story.append(Paragraph("C. Kuantum Bilgisayar Neyi Kırıyor? (Shor Algoritması)", h2_style))
    story.append(Paragraph(
        "Bugün bankacılıkta kullanılan RSA'nın güvencesi şudur: Bilgisayara 300 basamaklı iki dev asal sayı verirsiniz, saniyenin binde birinde bunları çarpar: A × B = C. "
        "Ancak saldırgana sadece devasa 'C' sayısını verip <i>'Hadi bunun hangi iki asal sayının çarpımı olduğunu bul (çarpanlarına ayır)'</i> derseniz, dünyadaki tüm süper bilgisayarlar bir araya gelse milyonlarca yıl bulamaz!<br/>"
        "<b>Kuantum Tehlikesi:</b> 1994 yılında Peter Shor, kuantum bilgisayarların atomik süperpozisyon gücünü kullanan bir algoritma buldu (<b>Shor Algoritması</b>). "
        "Normal bir bilgisayarda trilyonlarca adım süren çarpanlara ayırma bulmacasını, bir kuantum bilgisayar <b>dakikalar içinde</b> çözer! "
        "Yani yeterli güçte bir kuantum bilgisayar üretildiği gün RSA tek tuşla çökecektir.",
        body_style
    ))

    story.append(Paragraph("D. 'Şimdi Topla, Sonra Çöz' (Harvest Now, Decrypt Later - HNDL) Riski", h2_style))
    story.append(Paragraph(
        "Jüri sorabilir: <i>'Kuantum bilgisayarlar henüz tam yapılmadı, neden acele ediyoruz?'</i><br/>"
        "Cevap: Düşman istihbarat servisleri bugün internetten akan askeri, diplomatik ve bankacılık şifreli verilerini devasa veri merkezlerinde depolamaktadır. "
        "Amaçları, 5-10 yıl sonra kuantum bilgisayarı açtıklarında bu arşivlerin şifresini çözmektir. Bu yüzden kuantum sonrası kriptografiye (PQC) <b>hemen bugün</b> geçmek milli bir zorunluluktur!",
        body_style
    ))

    story.append(Paragraph("E. Kafes Tabanlı Kriptografi (Module-LWE) ve NIST FIPS 203 Standardı", h2_style))
    story.append(Paragraph(
        "Bilim insanları düşündü: Kuantum bilgisayarların bile çözemediği bir matematik problemi var mı? Buldular: <b>Kafes Problemleri (Lattice-Based Cryptography)</b>.<br/>"
        "Çok boyutlu uzayda devasa bir kafes (tel örgü) düşünün. Kafesin düğüm noktalarına bilerek küçük rastgele gürültüler (hatalar) eklenir (<b>Learning With Errors - LWE</b>). "
        "Shor algoritması çarpanlara ayırmayı çözer ama bu çok boyutlu kafes gürültüsünü çözemez! "
        "NIST, 13 Ağustos 2024'te bu kafes matematiğine dayalı algoritmayı <b>FIPS 203 (ML-KEM)</b> adıyla resmi dünya standardı ilan etmiştir.",
        body_style
    ))

    story.append(make_callout(
        "💡 JÜRİYE ÇOK KRİTİK CEVAP: Kuantum Bilgisayar Neden Kafes Şifresini Kıramaz?",
        "Jüri 'Shor algoritması kafesi neden çözemiyor?' derse cevabın: <i>'Hocam, Shor algoritması matematiksel periyot bulma (Fourier dönüşümü) mantığıyla çalışır. Asal çarpanlara ayırmada ve ayrık logaritmada periyodik bir yapı vardır. Ancak Kafes Tabanlı Kriptografide çok boyutlu uzayda periyodik olmayan rastgele hata vektörleri eklendiği için kuantum bilgisayar periyot bulamaz ve çözümsüz kalır.'</i> Bu açıklama jüriden tam puan alır!",
        kind="success"
    ))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 3: BÖLÜM 2: DARBOĞAZ: POLİNOM ÇARPIMI VE 23² BİNOM HİLESİ
    # =========================================================================
    story.append(Paragraph("2. DARBOĞAZ: POLİNOM ÇARPIMI VE 23² BİNOM AÇILIMI HİLESİ", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("A. ML-KEM'deki Büyük Darboğaz Nedir?", h2_style))
    story.append(Paragraph(
        "ML-KEM algoritması sayıları tek tek çarpmaz; her biri <b>256 terimli devasa harfli polinomları</b> (c₀ + c₁X + c₂X² + ... + c₂₅₅X²⁵⁵) birbiriyle çarpar. "
        "Bilgisayarlar harfli cebir işlemlerinden nefret eder. Standart okul çarpması (Schoolbook) 256 × 256 = <b>65.536 adet çarpma işlemi</b> gerektirir! "
        "Bu durum özellikle akıllı prizler, sayaçlar ve mikrodenetleyiciler gibi küçük IoT cihazlarını felç eder.",
        body_style
    ))

    story.append(Paragraph("B. Senin Bulduğun Cebirsel Fikir: 23² Hilesi", h2_style))
    story.append(Paragraph(
        "8. sınıf özdeşlikler konusunu hatırlayalım. 23 sayısını (2x + 3) şeklinde bir polinom gibi düşünürsek ve karesini alırsak:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>(2x + 3)² = 4x² + 12x + 9</b><br/>"
        "Buradaki katsayılar sırasıyla <b>[4, 12, 9]</b>'dur. Şimdi x yerine 10 koyduğumuzu hayal edelim ve ilkokuldaki gibi <b>sağdan sola elde taşıyalım</b>:<br/>"
        "• 9 birler basamağında aynen kalır.<br/>"
        "• 12'nin 2'si onlar basamağında kalır, 1 sola (yüzler basamağına) elde olarak taşar.<br/>"
        "• Yüzler basamağında 4 vardı; 4 + 1 = 5 olur.<br/>"
        "• Basamakları yan yana koyduğumuzda: <b>529</b> çıkar! Gerçekten de 23² = 529'dur!",
        body_style
    ))

    story.append(Paragraph("C. Büyük Sezgi: Sayılar Polinomdur, Polinomlar Sayıdır!", h2_style))
    story.append(Paragraph(
        "İşte projenin en büyük felsefesi buradadır: <b>Sayılar ile polinomlar aslında aynı şeydir!</b> "
        "Aralarındaki tek fark 'elde taşıma' (carry) kuralıdır. Bilgisayar işlemcileri harfli polinomlarla uğraşırken zorlanır ama "
        "<b>büyük tamsayıları donanımsal olarak ışık hızında çarpar!</b>",
        body_style
    ))

    story.append(Paragraph("D. Kronecker İkamesi (Leopold Kronecker, 1882) Nedir?", h2_style))
    story.append(Paragraph(
        "Alman matematikçi Leopold Kronecker 1882 yılında şunu önerdi: İki polinomu çarpmak yerine, x yerine öyle büyük bir sayı koyalım ki "
        "(örneğin 2 üzeri bir kuvvet), harfli polinom <b>tek bir devasa sayıya</b> dönüşsün! "
        "İşlemci bu iki dev sayıyı tek bir çarpma vuruşuyla çarpsın. Sonuç sayısını o kuvvetin bloklarına dilimleyerek çarpım polinomunun katsayılarını geri okuyalım.",
        body_style
    ))

    story.append(Paragraph("E. Standart (Klasik) Pozitif Kronecker Neden IoT İçin Kötüdür?", h2_style))
    story.append(Paragraph(
        "Klasik literatür katsayıları hep pozitif kabul eder ([0, 3328]). Çarpma sırasında 256 katsayı üst üste bindiğinde sayılar devasa boyutlara ulaşır. "
        "Katsayılar birbirinin basamağına taşmasın diye blok başına <b>en az 32 bit</b> ayırmak zorunda kalırlar. "
        "256 katsayı × 32 bit = <b>8192 BİTLİK DEV BİR SAYI!</b><br/>"
        "8192 bitlik bir sayıyı küçük bir mikrodenetleyicinin (ESP32) hafızasında tutmak imkansızdır; RAM'i şişirir ve kilitler.",
        body_style
    ))

    # Karşılaştırma Kutusu
    comp_data = [
        [Paragraph("İşlem Adımı", table_header), Paragraph("Senin 23² Binom Açılımı Hilen", table_header), Paragraph("Kronecker İkamesi Algoritması", table_header)],
        [Paragraph("1. Paketleme", table_cell_bold), Paragraph("23 sayısı ➔ (2x + 3) polinomu", table_cell), Paragraph("256 katsayılı polinom ➔ 2²² tabanında dev sayı", table_cell)],
        [Paragraph("2. Çarpma", table_cell_bold), Paragraph("(2x+3)² = 4x² + 12x + 9", table_cell), Paragraph("İki dev tamsayı donanımda tek hamlede çarpılır", table_cell)],
        [Paragraph("3. Açma (Unpack)", table_cell_bold), Paragraph("Sağdan sola elde taşıma (12'den 1 sola taşar)", table_cell), Paragraph("Sağdan sola 22-bitlik bloklar kesilir, ödünç alınır", table_cell)],
        [Paragraph("4. Nihai Sonuç", table_cell_bold), Paragraph("529 (Tam karesi)", table_cell), Paragraph("Çarpım polinomunun 256 katsayısı", table_cell)]
    ]
    t_comp = Table(comp_data, colWidths=[100, 205, 206])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_BLUE),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_comp)

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 4: BÖLÜM 3: KORKUNÇ FORMÜLLER VE MATEMATİKSEL İSPAT
    # =========================================================================
    story.append(Paragraph("3. KORKUNÇ GÖRÜNEN FORMÜLLERİN ANLAMI VE MATEMATİKSEL İSPAT (TEOREM 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("A. Formül 1: R_q = Z_q[X] / (X²⁵⁶ + 1),  q = 3329", h2_style))
    f1_desc = (
        "• <b>X²⁵⁶:</b> Polinomun 256 terimi vardır (c₀ + c₁X + ... + c₂₅₅X²⁵⁵). Bunu <b>256 vagonlu bir tren</b> gibi düşünün.<br/>"
        "• <b>q = 3329 (Saat Matematiği / Mod):</b> Sayı 3329'u aşarsa 3329 çıkarılır; saat 13 olduğunda aslında saat 1 dememiz gibidir.<br/>"
        "• <b>X²⁵⁶ + 1 = 0 ➔ X²⁵⁶ = -1 (Negasiklik İndirgeme):</b> Çarpma yaparken 256'yı aşan bir terim çıkarsa (örneğin X²⁵⁶), yerine <b>-1</b> yazılır! "
        "Örnek: X²⁵⁷ terimi çıkarsa, bu aslında X²⁵⁶ · X = (-1) · X = <b>-X</b> olur. "
        "Yani 256 vagonu aşan yolcular trenin en başına ama <b>ters işaretle (negatif)</b> binerler! Polinom asla 256 terimden uzun olamaz!"
    )
    story.append(make_box([Paragraph(f1_desc, math_box_style)], bg_color=C_LIGHT_BG, border_color=C_BORDER, padding=6))
    story.append(Spacer(1, 4))

    story.append(Paragraph("B. Formül 2: Merkezlenmiş Gösterim ([-1664, +1664])", h2_style))
    f2_desc = (
        "Sayıları klasik saat gibi hep pozitif [0, 3328] arasında tutmak yerine, sıfırı ortaya alıyoruz. "
        "3329'un yarısı 1664'tür. Sayı 1664'ten büyükse (örneğin 3328), 3328 - 3329 = <b>-1</b> diyoruz. "
        "Böylece sayılar kocaman devasa sayılar olmak yerine, sıfırın sağında ve solunda minik sayılara dönüşür: <b>[-1664, +1664]</b>."
    )
    story.append(make_box([Paragraph(f2_desc, math_box_style)], bg_color=C_LIGHT_BG, border_color=C_BORDER, padding=6))
    story.append(Spacer(1, 4))

    story.append(Paragraph("C. Formül 3: Gizli Vektör |s| ≤ η ≤ 3 (Projemizin Asıl Sırrı!)", h2_style))
    f3_desc = (
        "ML-KEM standardında iki polinom çarpılır: Biri internetten gelen açık matristir (katsayıları ±1664 olabilir). "
        "Ama diğeri kullanıcının kendi <b>gizli anahtarıdır (s)</b>! FIPS 203 standardı kuralı gereği gizli anahtarın katsayıları asla 3'ten büyük olamaz: "
        "<b>{-3, -2, -1, 0, 1, 2, 3}</b>.<br/>"
        "Biz şunu fark ettik: <i>'Çarpanlardan biri küçücükse (|s| ≤ 3), çarpım sonucu da küçük kalır!'</i>"
    )
    story.append(make_box([Paragraph(f3_desc, math_box_style)], bg_color=C_LIGHT_BG, border_color=C_BORDER, padding=6))
    story.append(Spacer(1, 4))

    story.append(Paragraph("D. Teorem 1: 22-Bit Sınırının Çıkarılışı (ℓ_min = 22)", h2_style))
    f4_desc = (
        "Jüri kesinlikle formülü soracaktır: <b>ℓ_min = ⌊log₂(n · A · η)⌋ + 2</b>. Matematiksel hesabı çok basittir:<br/>"
        "• <b>n = 256</b> (polinomda 256 terim var, çarpılınca en fazla 256 çarpım üst üste biner).<br/>"
        "• <b>A = 1664</b> (açık matrisin merkezlenmiş en büyük katsayısı).<br/>"
        "• <b>η = 3</b> (gizli anahtarın en büyük katsayısı).<br/>"
        "Hepsini çarpalım: 256 × 1664 × 3 = <b>1.277.952</b>.<br/>"
        "Çarpım sonucunda bir katsayı mutlak değerce en fazla 1 milyon 277 bin olabilir! Bilgisayarda bu sayıyı saklamak için kaç bit gerekir?<br/>"
        "• 2²⁰ = 1.048.576 (küçük kalır, taşar).<br/>"
        "• 2²¹ = 2.097.152 (yeter, sığar!).<br/>"
        "• Bir bit de pozitif/negatif işareti için ekleriz: 21 + 1 = <b>22 BİT!</b><br/>"
        "Standart yöntem 32 bit ayırıyordu (8192 bit). Biz 22 bite indirerek <b>5632 bit (%34 bellek tasarrufu)</b> sağladık!"
    )
    story.append(make_box([Paragraph(f4_desc, math_box_style)], bg_color=C_ICE_BG, border_color=C_CYAN, padding=6))
    story.append(Spacer(1, 4))

    story.append(make_callout(
        "⚠️ JÜRİNİN EN ÇOK ZORLAYACAĞI SORU: Formüldeki '+2' Nereden Geliyor?",
        "Jüri 'Neden logaritmanın üzerine 2 eklediniz?' diyecektir. Cevabın: <i>'Hocam, logaritma tamsayı tabanı ⌊log₂(...)⌋ aldığımız için kesirli kısmı yukarı yuvarlamak adına 1 ekleriz. İkinci 1 ise sonucun negatif katsayılarını (işaretini) saklamak için gereken işaret bitidir (Two's complement sign bit). Böylece toplamda +2 eklenir ve 20 + 2 = 22 bit bulunur.'</i>",
        kind="warn"
    ))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 5: BÖLÜM 4: 5 BÜYÜK BİLİMSEL KANIT VE DENEYLERİMİZ
    # =========================================================================
    story.append(Paragraph("4. JÜRİYİ BÜYÜLEYECEK 5 BÜYÜK BİLİMSEL KANITIMIZ", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("1. Kanıt: 200.000 Bağımsız Test ile Taşma Doğrulaması", h2_style))
    story.append(Paragraph(
        "Teorik olarak çıkardığımız 22 bit sınırını doğrulamak için bilgisayarda <b>200.000 bağımsız rastgele test</b> yaptık. "
        "22 bit genişliğinde 200.000 testin hiçbirinde tek bir katsayı bile taşmadı (%100 matematiksel doğruluk). "
        "Ayrıca Merkezi Limit Teoremi'ne dayalı olasılık modelimiz (Model 2), taşma olasılıklarını önceden tahmin etmede %100 başarılı oldu.",
        body_style
    ))

    story.append(Paragraph("2. Kanıt: H4 Güvenlik Açığı Deneyi (Neden 20 Bit Yapamayız?)", h2_style))
    story.append(Paragraph(
        "Jüri kesinlikle soracaktır: <i>'Madem 22 bit yaptınız, neden 20 bit yapmadınız? Daha çok tasarruf etmez miydiniz?'</i><br/>"
        "İşte projenin en büyük bilimsel keşfi buradadır:<br/>"
        "Kutucukları 20 bit yaparsanız hafızadan tasarruf edersiniz ama <b>GÜVENLİK ÇÖKER!</b><br/>"
        "Çünkü bir saldırgan katsayıları bilerek en uç değerlerde (+1664 ve -1664) olan özel tuzak şifreli metinler gönderir. "
        "Tuzak polinom çarpıldığında sonuç 20 bite sığmaz ve <b>TAŞAR (overflow)</b>. Taşma olunca alıcı şifreyi çözerken hata üretir.<br/>"
        "<b>En Büyük Sır:</b> Hatanın çıkıp çıkmaması tamamen kurbanın gizli anahtarının büyüklüğüne (<b>||s||₁ normuna</b>) bağlıdır! "
        "Saldırgan hangi şifreli metinlerin hata verdiğini sayarak kurbanın gizli anahtarını adım adım çalar! "
        "Yani 22 bit sadece bir matematik kuralı değil; <b>aşılırsa anahtarın sızdığı kırmızı güvenlik çizgisidir!</b>",
        body_style
    ))

    story.append(Paragraph("3. Kanıt: Hız Karşılaştırması ve Bilimsel Dürüstlük", h2_style))
    story.append(Paragraph(
        "Büyük tamsayı çarpımında 22-bit paketleme standart 32-bite göre <b>2,05 kat daha hızlıdır</b>. "
        "Ancak uçtan uca tüm ML-KEM sürecinde NIST'in resmi NTT yöntemi daha hızlı kalmıştır. Çünkü sayıları paketleyip geri açmak ek süre alır. "
        "Jüriye dürüstçe söyledik: <i>'Kronecker NTT'nin yerini almak için değil; NTT donanımı bulunmayan ultra-düşük RAM'li IoT çiplerinde en iyi alternatif olmak için tasarlanmıştır.'</i>",
        body_style
    ))

    story.append(Paragraph("4. Kanıt: PQC-Drop (Çalışan Güvenli Dosya Aktarım Yazılımı)", h2_style))
    story.append(Paragraph(
        "Projeyi sadece formülde bırakmadık. İki bilgisayar arasında çalışan <b>PQC-Drop</b> adında bir güvenli dosya aktarım programı geliştirdik. "
        "Dosyayı AES-256 kilitlerken, anahtarı bizim Kronecker motorumuz taşıdı. Wireshark ile ağ paketlerini yakalayıp analiz ettik; kuantum korumasını şeffafça doğruladık.",
        body_style
    ))

    story.append(Paragraph("5. Kanıt: Gerçek ESP32 Donanım Doğrulaması", h2_style))
    story.append(Paragraph(
        "Simülasyonda kalmayıp algoritmamızı C diliyle fiziksel bir <b>ESP32 çipine</b> yükledik. "
        "Çipin donanım saat sayacını okuyarak okul yöntemiyle %100 aynı katsayıları ürettik ve ara dizileri kaldırarak <b>768 baytlık mikro bellek sınırında</b> çalıştığını ispatladık.",
        body_style
    ))

    story.append(make_callout(
        "💡 BİLİMSEL DÜRÜSTLÜK KURALI: Jüriyi En Çok Etkileyen Şey!",
        "TÜBİTAK jürisi her şeyi mükemmel gösteren öğrencilere şüpheyle bakar. Bizim raporumuzda NTT'nin bazı durumlarda daha hızlı olduğunu dürüstçe beyan etmemiz ve 20 bitin güvenlik açığı ürettiğini deneysel olarak göstermemiz jürinin en çok takdir edeceği bilimsel olgunluktur!",
        kind="info"
    ))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 6: BÖLÜM 5: GERÇEK DONANIM DENEYİ (ESP32 MİKRODENETLEYİCİSİ)
    # =========================================================================
    story.append(Paragraph("5. GERÇEK DONANIM TESTİ (ESP32 MİKRODENETLEYİCİSİ)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("A. Neden Simülasyon Yetmedi, Neden Fiziksel Çipe İndik?", h2_style))
    story.append(Paragraph(
        "Bilgisayarınızda 16 GB RAM vardır; orada bellek darboğazını göremezsiniz. "
        "Fakat akıllı şehirlerde, askeri sensörlerde veya dronelarda kullanılan <b>ESP32 gibi çiplerde sadece 512 KB RAM</b> vardır! "
        "Biz algoritmamızın gerçek bir IoT çipinde çalışıp çalışmadığını kanıtlamak için kodu C/C++ ile fiziksel ESP32'ye flashladık.",
        body_style
    ))

    story.append(Paragraph("B. 24-Bit Comba Katsayı Akümülatörü Algoritmamız", h2_style))
    story.append(Paragraph(
        "• <b>Standart Okul Çarpması:</b> İki polinomu çarparken aradaki çarpımları saklamak için hafızada 511 katsayılık dev ara diziler açmak zorundadır.<br/>"
        "• <b>Bizim Yöntemimiz (24-bit Comba):</b> Biz ara dizi açmayız! İki polinomun katsayılarını tek tek çarpıp anında bir kumbara gibi 64-bitlik akümülatörde toplarız. "
        "Her katsayı 24 bit (tam 3 bayt) olduğu için 256 katsayı hafızada 256 × 3 = <b>tam 768 bayt</b> yer kaplar!",
        body_style
    ))

    story.append(Paragraph("C. ESP32 Donanım Test Metodolojisi", h2_style))
    story.append(Paragraph(
        "• <b>İşlemci:</b> Espressif ESP32 (Xtensa LX6 çift çekirdek, 80 MHz)<br/>"
        "• <b>Ölçüm Aracı:</b> Doğrudan işlemcinin iç donanım saat register'ı: <code>esp_cpu_get_cycle_count()</code>.<br/>"
        "• <b>Test Sayısı:</b> 100 bağımsız test döngüsü çalıştırıldı ve ortalaması alındı.",
        body_style
    ))

    story.append(Paragraph("D. Gerçek ESP32 Ölçüm Sonuçları Tablosu", h2_style))
    esp_table_data = [
        [Paragraph("Yöntem", table_header), Paragraph("Saat Çevrimi (Cycles)", table_header), Paragraph("Çalışma Süresi", table_header), Paragraph("Doğruluk", table_header), Paragraph("Yerel Bellek Tüketimi", table_header)],
        [
            Paragraph("<b>1. Standart Okul Yöntemi</b>", table_cell_bold),
            Paragraph("677.956 çevrim", table_cell),
            Paragraph("8.473 µs (8.4 ms)", table_cell),
            Paragraph("<b>%100 Eşleşme</b>", table_cell_bold),
            Paragraph("511 katsayı ara tampon (RAM şişer)", table_cell)
        ],
        [
            Paragraph("<b>2. Merkezlenmiş Kronecker / Comba</b>", table_cell_bold),
            Paragraph("841.234 çevrim", table_cell),
            Paragraph("10.514 µs (10.5 ms)", table_cell),
            Paragraph("<b>%100 Eşleşme</b>", table_cell_bold),
            Paragraph("<b>768 Bayt (Ara tamponsuz!)</b>", table_cell_bold)
        ]
    ]
    t_esp = Table(esp_table_data, colWidths=[125, 105, 95, 75, 111])
    t_esp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_BLUE),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,1), (3,-1), 'CENTER'),
    ]))
    story.append(t_esp)
    story.append(Spacer(1, 6))

    story.append(Paragraph("E. Sonuçların Yorumu: Ne Kazandık?", h2_style))
    story.append(Paragraph(
        "İki yöntem de <b>%100 birebir aynı katsayıları</b> üretti. Süre olarak okul yöntemi biraz daha hızlı olsa da (8.4 ms vs 10.5 ms), "
        "bizim yöntemimiz <b>511 elemanlık ara hafıza tamponunu sıfırladı</b> ve mikrodenetleyicinin sınırlı RAM'ini koruyarak <b>768 baytlık ultra-düşük bellekle</b> çalışmayı başardı!",
        body_style
    ))

    story.append(make_callout(
        "💡 JÜRİYE VURUCU DONANIM CEVABI: 'Neden Hızlanmadı?'",
        "Jüri 'ESP32'de süre neden daha az çıkmadı?' diye sorarsa: <i>'Hocam, ESP32 32-bit bir işlemcidir. Bizim katsayılarımız 24-bit olduğu için Xtensa mimarisinde 32-bitlik registerlara taşınırken küçük bir dönüştürme maliyeti oluşur. Ancak bizim amacımız hız rekoru kırmak değil; 512 KB RAM'li mikrodenetleyicilerde hafızayı şişiren 511 katsayılık ara tamponu ortadan kaldırıp 768 baytlık sabit bellekle çalışabilmektir.'</i> Bu cevap jüriden alkış alır!",
        kind="success"
    ))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 7: BÖLÜM 6: EN KRİTİK 10 JÜRİ SORUSU VE CEVAPLARI (1-5)
    # =========================================================================
    story.append(Paragraph("6. EN KRİTİK 10 JÜRİ SORUSU VE 9. SINIF CEVAPLARI (KISIM 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    qa_1_5 = [
        ("1. Yeni bir şifreleme algoritması mı icat ettiniz?",
         "Hayır değerli jüri üyem. Yeni bir şifreleme algoritması uydurmadık; çünkü kriptografide güvenliği kanıtlanmamış yeni şifreler kullanılmaz. "
         "Biz NIST'in 13 Ağustos 2024'te ilan ettiği resmi dünya standardı FIPS 203'ü (ML-KEM) temel aldık. Standardın kalbindeki en ağır işlem olan "
         "256 terimli polinom çarpımını matematiksel olarak optimize ettik."),

        ("2. Kronecker ikamesini dünyada ilk siz mi buldunuz?",
         "Hayır, Leopold Kronecker bu yöntemi 1882 yılında buldu. Ancak klasik Kronecker ikamesi katsayıları pozitif alarak 32 bitlik devasa sayılar üretir. "
         "ML-KEM standardında gizli anahtarın katsayılarının [-3, +3] sınırını fark ederek katsayıları sıfır etrafında merkezleyen, kutucukları 32 bitten 22 bite "
         "indiren ve fiziksel ESP32 çipinde 768 bayt yerel bellek modelini kuran dünyada ilk biziz!"),

        ("3. Neden 22 bit? 20 bit yapsak hafızadan daha çok tasarruf etmez miyiz?",
         "Hafızadan tasarruf ederiz ama GÜVENLİK ÇÖKER! 20 bit yaparsak katsayılar taşar ve şifre çözülürken hata verir. "
         "Hatanın çıkıp çıkmaması kurbanın gizli anahtarının büyüklüğüne (||s||₁ normuna) bağlı hale gelir. Saldırgan tuzak şifreli metinler yollayarak gizli anahtarı "
         "adım adım çalar! H4 deneyimizle 22 bitin altına inilemeyeceğini ilk kez güvenlikle kanıtladık."),

        ("4. Resmi standartta NTT varken Kronecker ikamesine ne gerek var?",
         "NTT (Number Theoretic Transform) çok hızlıdır ama çalışması için modül sayısının özel bir asal sayı olması ve yüksek RAM gerekir. "
         "Evimizdeki akıllı prizlerde, su sayaçlarında veya IoT sensörlerinde NTT donanımı yoktur. Kronecker ikamesi bu minik cihazlarda standart tamsayı "
         "çarpıcılarını kullanarak 768 baytlık ultra-düşük RAM ile çalışmayı sağlar."),

        ("5. Kendi aranızda iş bölümünü nasıl yaptınız?",
         "Halil yazılım mimarisi, ESP32 donanım testleri, C/C++ kodlaması ve PQC-Drop ağ protokolünü yürüttü; diğer arkadaşımız teorik ispatlar, olasılık modelleri "
         "ve rapor anlatımını üstlendi. Ancak ikimiz de projenin her satırını, her formülünü ve her donanım testini tek başımıza savunabilecek düzeyde hakimiz.")
    ]

    for q, a in qa_1_5:
        qa_card = [
            [Paragraph(f"<b>Soru:</b> {q}", ParagraphStyle('QS', fontName='Roboto-Bold', fontSize=8.5, leading=11, textColor=C_NAVY))],
            [Paragraph(f"<b>9. Sınıf Cevabı:</b> {a}", ParagraphStyle('AS', fontName='Roboto', fontSize=8.3, leading=11.5, textColor=C_DARK))]
        ]
        t_q = Table(qa_card, colWidths=[printable_width])
        t_q.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.6, C_BORDER),
            ('LINEBELOW', (0,0), (-1,0), 0.4, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_q)
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 8: BÖLÜM 7: EN KRİTİK 10 JÜRİ SORUSU VE CEVAPLARI (6-10)
    # =========================================================================
    story.append(Paragraph("7. EN KRİTİK 10 JÜRİ SORUSU VE 9. SINIF CEVAPLARI (KISIM 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    qa_6_10 = [
        ("6. ESP32 donanım testinde çalışma süresi neden hızlanmadı?",
         "Süre olarak okul yöntemiyle oldukça yakın çıktık (8.4 ms vs 10.5 ms). Çünkü ESP32 32-bit bir işlemcidir ve 24-bitlik Comba katsayılarını "
         "akümülatöre alırken dönüştürme yapar. Ancak bizim asıl amacımız hız değil BELLEK TASARRUFUDUR: Standart yöntem hafızada 511 katsayılık kocaman "
         "ara dizi açarken, bizim yöntemimiz sıfır ara tamponla 768 baytta çalışmayı başarmıştır."),

        ("7. Projede Yapay Zekâ (AI) kullandınız mı?",
         "Evet jüri üyem, raporumuzda ve proje günlüğümüzde de dürüstçe beyan ettik. Kodların testlerini hazırlarken, dokümantasyonda ve grafik çizimlerinde "
         "asistan olarak yararlandık. Ancak matematiksel hipotez, 22-bit ispatı, ESP32 donanım ölçümleri ve bilimsel kararlar tamamen bize aittir."),

        ("8. Model 2 nedir, neden Merkezi Limit Teoremi kullandınız?",
         "Polinom katsayıları rastgele dağıldığı için, 256 terim çarpılıp toplandığında toplamın dağılımı Merkezi Limit Teoremi gereği Gauss (Normal) dağılımına "
         "yaklaşır. Model 2, deneyi yapmadan önce hangi bit genişliğinde ne kadar taşma hatası çıkacağını önceden hesaplayan olasılık formülümüzdür. "
         "200.000 test tam formülümüzün öngördüğü gibi çıkmıştır."),

        ("9. PQC-Drop ne işe yarıyor, nerede çalışıyor?",
         "PQC-Drop, geliştirdiğimiz matematik motorunu gerçek hayata uyarladığımız bir dosya aktarım programıdır. İki bilgisayar arasında dosya gönderirken "
         "dosyayı AES-256 ile kilitler; AES anahtarını ise bizim Kronecker motorumuz kuantum korumalı olarak taşır. Wireshark ile paketleri yakalayarak "
         "ağ trafiğinde anahtarın asla görünmediğini kanıtladık."),

        ("10. Bu proje Türkiye için neden önemli?",
         "Ülkemizin TSK verileri, MİT haberleşmesi, İHA/SİHA telemetri hatları ve e-Devlet altyapısı kuantum bilgisayarlar gelmeden önce kuantum sonrası "
         "kriptografiye geçmek zorundadır. Yerli donanımlarda (örneğin yerli mikroçiplerde) çalışabilecek ultra-düşük RAM'li şifreleme motorları geliştirmek "
         "Siber Vatan güvenliğimiz için hayati bir adımdır.")
    ]

    for q, a in qa_6_10:
        qa_card = [
            [Paragraph(f"<b>Soru:</b> {q}", ParagraphStyle('QS2', fontName='Roboto-Bold', fontSize=8.5, leading=11, textColor=C_NAVY))],
            [Paragraph(f"<b>9. Sınıf Cevabı:</b> {a}", ParagraphStyle('AS2', fontName='Roboto', fontSize=8.3, leading=11.5, textColor=C_DARK))]
        ]
        t_q = Table(qa_card, colWidths=[printable_width])
        t_q.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.6, C_BORDER),
            ('LINEBELOW', (0,0), (-1,0), 0.4, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_q)
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 9: BÖLÜM 8: 5 DAKİKALIK JÜRİ SUNUM PLANI
    # =========================================================================
    story.append(Paragraph("8. JÜRİ ÖNÜNDE 5 DAKİKALIK ÖRNEK SUNUM PLANI", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("Jüri karşısına çıktığında süreyi kusursuz yönetmek için şu 5 adımlı planı takip et:", body_style))

    pitch_data = [
        [Paragraph("Zaman", table_header), Paragraph("Sunum Bölümü", table_header), Paragraph("Konuşulacak Kilit Mesajlar", table_header)],
        [
            Paragraph("<b>1. Dakika</b>", table_cell_bold),
            Paragraph("<b>Giriş & Tehlike</b>", table_cell_bold),
            Paragraph("Kuantum bilgisayarların klasik RSA'yı kırma tehlikesi (Shor algoritması), 'Şimdi topla sonra çöz' riski ve NIST'in yeni FIPS 203 ML-KEM standardı.", table_cell)
        ],
        [
            Paragraph("<b>2. Dakika</b>", table_cell_bold),
            Paragraph("<b>Cebirsel Fikrimiz</b>", table_cell_bold),
            Paragraph("23² binom açılımından çıkan sezgimiz, Kronecker ikamesi ve katsayıları merkezleyerek tamsayıyı 32 bitten 22 bite indirme başarımız (%34 bellek tasarrufu).", table_cell)
        ],
        [
            Paragraph("<b>3. Dakika</b>", table_cell_bold),
            Paragraph("<b>İspat & Güvenlik</b>", table_cell_bold),
            Paragraph("Teorem 1 matematiksel ispatı (256 × 1664 × 3 = 1.277.952 ➔ 22 bit), 200.000 test ve 20 bite inildiğinde gizli anahtarın nasıl sızdığı (H4 deneyi).", table_cell)
        ],
        [
            Paragraph("<b>4. Dakika</b>", table_cell_bold),
            Paragraph("<b>Donanım & Ürün</b>", table_cell_bold),
            Paragraph("Fiziksel ESP32 çipinde 768 bayt mikro bellekle çalışan C kodumuz ve donanım register ölçümleri; iki bilgisayar arası dosyayı koruyan PQC-Drop yazılımı.", table_cell)
        ],
        [
            Paragraph("<b>5. Dakika</b>", table_cell_bold),
            Paragraph("<b>Sonuç & Kapanış</b>", table_cell_bold),
            Paragraph("Dürüst bilimsel sonuçlarımız (Büyük sayıda 2x hız, tam KEM'de dönüşüm bedeli), yerli siber güvenlik vizyonu, teşekkür ve jüri sorularına davet.", table_cell)
        ]
    ]
    t_pitch = Table(pitch_data, colWidths=[65, 120, 326])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_BLUE),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
    ]))
    story.append(t_pitch)
    story.append(Spacer(1, 10))

    story.append(Paragraph("🎯 Jüri Önünde Başarı Getirecek 4 Altın Davranış Kuralı", h2_style))
    tips = [
        "• <b>1. Asla Ezber Konuşma:</b> Jüriye slayt okuma; sanki bir arkadaşına 23² hilesini anlatıyormuş gibi rahat, göz teması kurarak konuş.",
        "• <b>2. Bilmediğin Yerde 'Bilmiyorum' Demekten Korkma:</b> Bilmediğin teorik bir detay sorulursa sallama: <i>'Hocam bu konuyu araştırmalarımızda incelemedik ama literatür notlarımıza mutlaka ekleyip araştıracağım'</i> de.",
        "• <b>3. Tahtayı ve Kalemi Kullan:</b> Jüri formülü sorarsa konuşarak anlatmaya çalışma; tahtaya kalkıp <code>256 × 1664 × 3 = 1.277.952</code> yaz! Tahtaya kalkan öğrenci jürinin gözünde hemen tam not alır.",
        "• <b>4. Donanımı Masaya Koy:</b> Sunum masasına ESP32 çipini koy; jüriye <i>'Hocam bu gördüğünüz çipte 768 baytta kuantum güvenliğini çalıştırdık'</i> diyerek çipi gösterin."
    ]
    for tip in tips:
        story.append(Paragraph(tip, bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # SAYFA 10: BÖLÜM 9: MASTER SÖZLÜK VE TEK BAKIŞTA ZİHİN HARİTASI
    # =========================================================================
    story.append(Paragraph("9. TEK BAKIŞTA PROJE ZİHİN HARİTASI VE MASTER SÖZLÜK", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceBefore=0, spaceAfter=8))

    vocab_data = [
        [Paragraph("Terim", table_header), Paragraph("9. Sınıf Seviyesinde Basit Tanımı", table_header), Paragraph("Projemizdeki Hayati Rolü", table_header)],
        [Paragraph("Kuantum Tehdidi", table_cell_bold), Paragraph("Kuantum bilgisayarların klasik RSA şifrelerini saniyeler içinde kırma riski.", table_cell), Paragraph("Neden bu projeyi yaptığımızın varoluş sebebi.", table_cell)],
        [Paragraph("Shor Algoritması", table_cell_bold), Paragraph("Kuantum bilgisayarda asal çarpanlara ayırmayı çözen formül.", table_cell), Paragraph("Klasik şifreleri yıkan ana tehdit algoritması.", table_cell)],
        [Paragraph("ML-KEM (FIPS 203)", table_cell_bold), Paragraph("NIST'in Ağustos 2024'te yayımladığı kuantuma dayanıklı dünya standardı.", table_cell), Paragraph("Temel aldığımız ve optimize ettiğimiz resmi standart.", table_cell)],
        [Paragraph("Kronecker İkamesi", table_cell_bold), Paragraph("Polinom katsayılarını tek bir dev sayıya paketleyip tek vuruşta çarpma hilesi.", table_cell), Paragraph("Polinom çarpımını hızlandırmak için kurduğumuz motor.", table_cell)],
        [Paragraph("23² Binom Açılımı", table_cell_bold), Paragraph("Binom katsayılarının sağdan sola elde taşınarak sayıya dönüşmesi.", table_cell), Paragraph("Projenin çıkış noktası ve açma algoritmasının temeli.", table_cell)],
        [Paragraph("Merkezlenmiş Gösterim", table_cell_bold), Paragraph("Sayıları [0, 3328] yerine sıfırın etrafında [-1664, 1664] olarak tutmak.", table_cell), Paragraph("Katsayıları küçülterek 32 bitten 22 bite inmemizi sağlayan sır.", table_cell)],
        [Paragraph("Teorem 1 (22 Bit)", table_cell_bold), Paragraph("Katsayıların çarpımda taşmaması için gereken en küçük alan sınırı.", table_cell), Paragraph("Matematiksel olarak ispatladığımız özgün sınır.", table_cell)],
        [Paragraph("H4 Güvenlik Deneyi", table_cell_bold), Paragraph("20 bite inilirse taşmaların kurbanın gizli anahtarını dışarı sızdırması.", table_cell), Paragraph("22 bitin altına inilemeyeceğinin güvenlik kanıtı.", table_cell)],
        [Paragraph("ESP32 Donanım Testi", table_cell_bold), Paragraph("Fiziksel IoT çipinde saat çevrimi register ölçümü.", table_cell), Paragraph("768 baytlık ultra-düşük RAM başarımızın gerçek kanıtı.", table_cell)],
        [Paragraph("PQC-Drop", table_cell_bold), Paragraph("AirDrop gibi iki bilgisayar arası kuantum korumalı dosya gönderme yazılımı.", table_cell), Paragraph("Teorinin çalışan somut bir ürüne dönüştüğünün kanıtı.", table_cell)]
    ]
    t_vocab = Table(vocab_data, colWidths=[100, 211, 200])
    t_vocab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_vocab)
    story.append(Spacer(1, 12))

    # Kapanış Kutusu
    closing_box = [
        Paragraph("<b>HALİL, BU PROJE SENİN EMEĞİN VE SENİN ESERİN!</b>", ParagraphStyle('CloseH', fontName='Roboto-Bold', fontSize=9.5, leading=13, textColor=C_NAVY, alignment=1, spaceAfter=3)),
        Paragraph("Jüri karşısına çıktığında unutma: Sen sadece bir yazılım yazmadın; kuantum sonrası kriptografinin resmi dünya standardını inceledin, "
                  "matematiksel bir teorem ispatladın, güvenlik açığı deneyini başarıyla tamamladın ve bunu fiziksel bir ESP32 çipinde çalıştırdın. "
                  "Bu bilgi ve özgüvenle jüriye anlatacağın her şey jüriyi etkileyecektir. Başarılar dileriz!", ParagraphStyle('CloseB', fontName='Roboto', fontSize=8.6, leading=12.2, textColor=C_DARK, alignment=1))
    ]
    story.append(make_box(closing_box, bg_color=C_SUCCESS_BG, border_color=C_SUCCESS_BORDER, padding=8))

    # Dokümanı Derle
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Öğrenim Kitabı PDF basariyla olusturuldu: {output_path}")

if __name__ == '__main__':
    out_pdf = "/home/halil/Documents/2204a/2204a-pqc-kronecker/docs/TUBITAK_2204A_MASTER_OGRENIM_VE_JURI_KITABI_10SAYFA.pdf"
    create_master_guide_pdf(out_pdf)
