#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÜBİTAK 2204-A Lise Araştırma Projeleri
PQC-Kronecker: Sıfırdan Mantık, Formül Öğrenim ve Jüri Savunma Kılavuzu (Master Birleşik Rehber)
Öğrenci: Halil Erdem Yanık (9. Sınıf Seviyesinde Tam Anlatım)
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
        self.saveState()
        self.setFont("Roboto", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Sayfa 1 dahil veya hariç düzenli başlıklar
        if self._pageNumber > 1:
            self.drawString(34, 815, "TÜBİTAK 2204-A — Master Öğrenim ve Jüri Savunma Rehberi (PQC-Kronecker)")
            self.drawRightString(561, 815, "Halil Erdem Yanık")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(34, 808, 561, 808)

            page_text = f"Sayfa {self._pageNumber} / {page_count}"
            self.drawRightString(561, 24, page_text)
            self.drawString(34, 24, "Kişisel Öğrenim ve Jüri Savunma Rehberi — 9. Sınıf Seviyesinde Formül ve Mantık")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(34, 34, 561, 34)

        self.restoreState()

def create_master_guide(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=34,
        rightMargin=34,
        topMargin=44,
        bottomMargin=44
    )

    c_primary = colors.HexColor("#0F172A")    # Koyu gece mavisi
    c_blue = colors.HexColor("#1D4ED8")       # Canlı ana başlık mavisi
    c_accent = colors.HexColor("#0369A1")     # Gökyüzü mavisi
    c_teal = colors.HexColor("#0D9488")       # Matematik kutusu rengi
    c_amber = colors.HexColor("#D97706")      # Formül kutusu rengi
    c_red = colors.HexColor("#DC2626")        # Güvenlik açığı rengi
    c_dark = colors.HexColor("#1E293B")       # Okuma metni
    c_bg_light = colors.HexColor("#F8FAFC")
    c_bg_blue = colors.HexColor("#EFF6FF")
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Roboto-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        alignment=1,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        fontName='Roboto',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'H1',
        fontName='Roboto-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_blue,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        fontName='Roboto-Bold',
        fontSize=10,
        leading=13,
        textColor=c_accent,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        fontName='Roboto',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=4
    )

    quote_style = ParagraphStyle(
        'Quote',
        fontName='Roboto-Italic',
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )

    math_box_style = ParagraphStyle(
        'MathBox',
        fontName='Roboto',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )

    table_header = ParagraphStyle(
        'TH',
        fontName='Roboto-Bold',
        fontSize=7.8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell_bold = ParagraphStyle(
        'TCB',
        fontName='Roboto-Bold',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark
    )

    table_cell = ParagraphStyle(
        'TC',
        fontName='Roboto',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark
    )

    story = []

    # ==================== KAPAK BAŞLIĞI ====================
    story.append(Spacer(1, 4))
    story.append(Paragraph("TÜBİTAK 2204-A LİSE ARAŞTIRMA PROJELERİ", ParagraphStyle('Tag', fontName='Roboto-Bold', fontSize=9, leading=11, textColor=c_teal, alignment=1, spaceAfter=3)))
    story.append(Paragraph("KULLANICI VE JÜRİ ORTAK ÖĞRENİM REHBERİ", title_style))
    story.append(Paragraph("<b>Proje:</b> Kuantum Sonrası Güvenli İletişimde Merkezlenmiş Kronecker İkamesi (NIST FIPS 203 ML-KEM)<br/><b>Öğrenci:</b> Halil Erdem Yanık · <b>Kapsam:</b> Sıfırdan Formül & Mantık Öğrenimi + 5 Bilimsel Kanıt + 10 Jüri Sorusu", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_blue, spaceBefore=2, spaceAfter=8))

    # ==================== KISIM 1: ASANSÖR KONUŞMASI ====================
    story.append(Paragraph("🎯 KISIM 1: 30 Saniyelik Asansör Konuşması (Büyük Resim)", h1_style))
    elevator_text = (
        "<b>\"Değerli jüri üyeleri;</b> bugün kullandığımız bankacılık ve internet şifreleri (RSA), kuantum bilgisayarlar "
        "tarafından (Shor algoritmasıyla) dakikalar içinde kırılabilecektir. NIST bu tehdide karşı Ağustos 2024'te resmi dünya standardı "
        "<b>ML-KEM</b>'i yayımladı. Ancak ML-KEM'in kalbinde bilgisayarları çok yoran 256 terimli polinom çarpımları vardır.<br/><br/>"
        "Biz bu projede, polinom katsayılarını tek bir dev sayıya paketleyip tek vuruşta çarpan <b>Kronecker ikamesini</b> inceledik. "
        "Katsayıları sıfır etrafında merkezleyerek gereken tamsayı genişliğini <b>32 bitten 22 bite indirdik (%34 bellek tasarrufu)</b>. "
        "Bu sınırın altına inilirse gizli anahtarın nasıl sızdığını ispatladık. Yöntemimizi güvenli dosya aktarımı yapan <b>PQC-Drop</b> yazılımında "
        "ve fiziksel <b>ESP32 çipinde 768 baytlık ultra-düşük RAM tamponuyla</b> başarıyla çalıştırdık.\""
    )
    t_box = Table([[Paragraph(elevator_text, quote_style)]], colWidths=[527])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_blue),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('PADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 6))

    # ==================== KISIM 2: KRİPTOGRAFİNİN TEMELİ ====================
    story.append(Paragraph("📖 KISIM 2: Kriptografinin En Temel Mantığı (Biz Neyi Korumaya Çalışıyoruz?)", h1_style))
    p_kripto = (
        "• <b>Simetrik Şifreleme (Örnek: AES-256):</b> Tek bir anahtar vardır. Dosyayı aynı anahtar kilitler ve açar. Çok hızlıdır ama anahtarı internetten karşı tarafa güvenle iletmek zordur.<br/>"
        "• <b>Asimetrik Şifreleme (Örnek: RSA, ML-KEM):</b> İki anahtar vardır: Açık anahtar (posta kutusunun deliği gibidir, herkes mektup atabilir) ve Gizli anahtar (sadece alıcıda olan kutu anahtarıdır).<br/>"
        "• <b>KEM (Anahtar Kapsülleme):</b> Büyük dosyayı ışık hızındaki AES kilitler; AES'in 256 bitlik minik anahtarını ise ML-KEM bir zarfın (kapsülün) içine koyup karşıya gönderir.<br/>"
        "• <b>Kuantum Tehdidi ve 'Şimdi Topla, Sonra Çöz' (HNDL):</b> Kuantum bilgisayar çıktığında Shor algoritması bugünkü RSA şifrelerini anında çözecektir. Saldırganlar bugünden şifreli devlet ve banka verilerini kaydedip saklamaktadır. Bu yüzden kuantum sonrası kriptografiye (PQC) bugünden geçmek zorundayız!"
    )
    story.append(Paragraph(p_kripto, body_style))
    story.append(Spacer(1, 6))

    # ==================== KISIM 3: RAPORDAKİ KORKUNÇ FORMÜLLER ====================
    story.append(Paragraph("📖 KISIM 3: Rapordaki Korkunç Görünen Formüllerin Anlamı ve İspatı", h1_style))
    story.append(Paragraph("Rapordaki matematiksel semboller 9. sınıf seviyesinde çok basit kurallardır:", body_style))

    f1_t = "<b>1. R_q = Z_q[X] / (X²⁵⁶ + 1),  q = 3329</b>"
    f1_d = (
        "• <b>X²⁵⁶:</b> Polinomun 256 tane katsayısı vardır. Bunu <b>256 vagonlu bir tren</b> gibi düşünün.<br/>"
        "• <b>q = 3329 (Saat Matematiği / Mod):</b> Sayı 3329'u aşarsa 3329 çıkarılır; saat 13'ün 1 olması gibidir.<br/>"
        "• <b>X²⁵⁶ = -1 (Negasiklik İndirgeme):</b> Çarpımda X²⁵⁶ çıkarsa yerine <b>-1</b> yazılır. "
        "Örn: X²⁵⁷ = -X olur. 256 vagonu aşan terimler <b>ters işaretle trenin başına döner</b>!"
    )
    t1 = Table([[Paragraph(f1_t, ParagraphStyle('F1', fontName='Roboto-Bold', fontSize=8.5, textColor=c_teal)), Paragraph(f1_d, math_box_style)]], colWidths=[160, 367])
    t1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_teal), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t1)
    story.append(Spacer(1, 4))

    f2_t = "<b>2. Merkezlenmiş Gösterim ([-1664, 1664])</b>"
    f2_d = (
        "Sayıları hep [0, 3328] arasında tutmak yerine sıfırı ortaya alıyoruz. 3329'un yarısı 1664'tür. "
        "Sayı 1664'ten büyükse (örneğin 3328), 3328 - 3329 = <b>-1</b> diyoruz. "
        "Böylece sayılar devasa olmak yerine sıfırın çevresinde minik sayılara dönüşür."
    )
    t2 = Table([[Paragraph(f2_t, ParagraphStyle('F2', fontName='Roboto-Bold', fontSize=8.5, textColor=c_amber)), Paragraph(f2_d, math_box_style)]], colWidths=[160, 367])
    t2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_amber), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t2)
    story.append(Spacer(1, 4))

    f3_t = "<b>3. Gizli Vektör |s| ≤ η ≤ 3 (Asıl Sır!)</b>"
    f3_d = (
        "ML-KEM'de çarpılan iki polinomdan biri açık matristir (±1664 olabilir). Ama diğeri <b>gizli anahtardır (s)</b>. "
        "FIPS 203 standardı gereği gizli anahtarın katsayıları asla 3'ü geçemez: <b>{-3, -2, -1, 0, 1, 2, 3}</b>. "
        "Bizim keşfimiz: <i>'Çarpanlardan biri küçücükse, çarpım sonucu da küçük kalır!'</i>"
    )
    t3 = Table([[Paragraph(f3_t, ParagraphStyle('F3', fontName='Roboto-Bold', fontSize=8.5, textColor=c_blue)), Paragraph(f3_d, math_box_style)]], colWidths=[160, 367])
    t3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_blue), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t3)
    story.append(Spacer(1, 4))

    f4_t = "<b>4. Teorem 1 (ℓ_min = 22 Bit İspatı)</b>"
    f4_d = (
        "Formül: ℓ_min = ⌊log₂(n · A · η)⌋ + 2. Matematiksel hesabı çok basittir:<br/>"
        "• n = 256 terim · A = 1664 katsayı · η = 3 gizli anahtar = <b>1.277.952</b>.<br/>"
        "• 2²⁰ = 1.048.576 (küçük kalır, sığmaz). 2²¹ = 2.097.152 (sığar!).<br/>"
        "• 1 bit de pozitif/negatif işareti için eklenir: 21 + 1 = <b>22 BİT!</b><br/>"
        "Standart yöntem 32 bit ayırıyordu (8192 bit dev sayı). Biz 22 bite indirerek <b>5632 bit (%34 tasarruf)</b> elde ettik."
    )
    t4 = Table([[Paragraph(f4_t, ParagraphStyle('F4', fontName='Roboto-Bold', fontSize=8.5, textColor=c_primary)), Paragraph(f4_d, math_box_style)]], colWidths=[160, 367])
    t4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_primary), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t4)
    story.append(Spacer(1, 6))

    # ==================== KISIM 4: 23² HİLESİ VE KRONECKER ====================
    story.append(Paragraph("📖 KISIM 4: 23² Hilesi ve Kronecker İkamesi (Senin Bulduğun Mantık)", h1_style))
    p_kron = (
        "<b>Senin Söylediğin Cebirsel Hile:</b> (2x + 3)² = 4x² + 12x + 9. Katsayılar [4, 12, 9]'dur. Sağdan sola elde taşırız: "
        "9 kalır, 12'nin 2'si kalır 1 sola taşar, 4+1=5 olur. Sonuç: <b>529</b>.<br/>"
        "<b>Kronecker İkamesi bunun ikiz kardeşidir:</b><br/>"
        "1. 256 terimli polinomda x yerine <b>2²²</b> yazarız. Polinom tek bir 5632 bitlik dev sayıya dönüşür.<br/>"
        "2. Bilgisayar bu iki dev sayıyı ilkokul çarpması gibi tek hamlede çarpar.<br/>"
        "3. Sonuç sayısından sağdan sola 22-bitlik blokları keserek katsayıları geri toplarız (eksi çıkarsa ödünç alırız)."
    )
    story.append(Paragraph(p_kron, body_style))
    story.append(Spacer(1, 6))

    # ==================== KISIM 5: 5 BÜYÜK BİLİMSEL KANIT ====================
    story.append(Paragraph("🔬 KISIM 5: Jüriyi Büyüleyecek 5 Büyük Bilimsel Kanıtımız", h1_style))
    k1 = "<b>1. Kanıt (ℓ_min = 22 Bit Taşma Sınırı):</b> 200.000 bağımsız test yaptık; tek bir katsayı bile taşmadı. Merkezi Limit Teoremi'ne dayalı olasılık modelimiz (Model 2) deneysel sonuçlarla birebir örtüştü."
    k2 = "<b>2. Kanıt (H4 Güvenlik Açığı Deneyi):</b> 20 bite inersek ne olur? Tuzak polinomlarla katsayılar taşar ve hata verir. Hatanın çıkması kurbanın gizli anahtarının büyüklüğüne (||s||₁) bağlıdır. Saldırgan anahtarı çalar! 22 bitin kırmızı güvenlik çizgisi olduğunu ispatladık."
    k3 = "<b>3. Kanıt (Hız ve Bilimsel Dürüstlük):</b> Büyük tamsayı çarpımında 22-bit paketleme standart 32-bite göre <b>2,05 kat daha hızlıdır</b>. Ancak uçtan uca ML-KEM'de paketleme süreleri nedeniyle NTT daha hızlıdır. Kronecker'in asıl gücü NTT donanımı olmayan IoT/mikroişlemcilerdedir."
    k4 = "<b>4. Kanıt (ESP32 Donanım Doğrulaması):</b> Simülasyonda kalmadık; C/C++ kodumuzu fiziksel ESP32 çipine yükledik. <code>esp_cpu_get_cycle_count()</code> ile donanım çevrimlerini ölçtük. Okul yöntemiyle %100 birebir aynı katsayıları ürettik ve ara dizileri kaldırarak <b>768 baytlık ultra-düşük RAM'de</b> çalıştık."
    k5 = "<b>5. Kanıt (PQC-Drop Yazılımı):</b> Teoriyi çalışan ürüne dönüştürdük. İki bilgisayar arası dosyayı AES-256 kilitlerken anahtarı bizim Kronecker motorumuz taşıdı. Wireshark PCAP analizleriyle kuantum güvenliği doğrulandı."
    for k in [k1, k2, k3, k4, k5]:
        story.append(Paragraph(k, body_style))
    story.append(Spacer(1, 4))

    # ==================== ESP32 TABLOSU ====================
    story.append(Paragraph("📊 Gerçek ESP32 Donanım Ölçüm Sonuçları (80 MHz, N=256, q=3329)", h2_style))
    esp_data = [
        [Paragraph("Yöntem", table_header), Paragraph("Ortalama Saat Çevrimi", table_header), Paragraph("Ortalama Süre", table_header), Paragraph("Doğruluk", table_header), Paragraph("Yerel Bellek", table_header)],
        [Paragraph("1. Standart Okul Yöntemi", table_cell_bold), Paragraph("677.956 çevrim", table_cell), Paragraph("8.473 µs", table_cell), Paragraph("%100 Eşleşme", table_cell), Paragraph("256 katsayı ara tampon", table_cell)],
        [Paragraph("2. Merkezlenmiş Kronecker / Comba", table_cell_bold), Paragraph("841.234 çevrim", table_cell), Paragraph("10.514 µs", table_cell), Paragraph("%100 Eşleşme", table_cell), Paragraph("<b>768 Bayt (Ara tamponsuz)</b>", table_cell)]
    ]
    t_esp = Table(esp_data, colWidths=[130, 105, 85, 80, 127])
    t_esp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('ALIGN', (1,1), (3,-1), 'CENTER'),
    ]))
    story.append(t_esp)
    story.append(Spacer(1, 8))

    # ==================== KISIM 6: EN KRİTİK 10 JÜRİ SORUSU ====================
    story.append(Paragraph("❓ KISIM 6: En Kritik 10 Jüri Sorusu ve 9. Sınıf Cevapları", h1_style))
    qa_list = [
        ("1. Yeni bir şifreleme algoritması mı icat ettiniz?",
         "Hayır jüri üyem. Yeni bir şifre icat etmedik; NIST'in resmi kuantum standardı FIPS 203'ü (ML-KEM) temel aldık. Standardın kalbindeki en ağır işlem olan 256 terimli polinom çarpımını optimize ettik."),

        ("2. Kronecker ikamesini ilk siz mi buldunuz?",
         "Hayır, Leopold Kronecker 1882'de buldu. Ancak ML-KEM'de gizli anahtarın [-3, 3] sınırını kullanarak katsayıları 32 bitten 22 bite indiren ve ESP32'de 768 bayt yerel bellek modelini kuran ilk biziz."),

        ("3. Neden 22 bit? 20 bit yapsak hafızadan daha çok tasarruf etmez miyiz?",
         "Tasarruf ederiz ama güvenlik çöker! 20 bit yaparsak katsayılar taşar ve hata üretir. Bu hata kurbanın gizli anahtarının büyüklüğüne bağlı olduğu için saldırgan gizli anahtarı sızdırabilir (H4 deneyimizle bunu kanıtladık)."),

        ("4. NTT varken Kronecker'e ne gerek var?",
         "NTT çok hızlıdır ama çalışması için özel matematiksel asal sayılar ve yüksek RAM gerekir. Akıllı priz, sayaç ve IoT çiplerinde NTT donanımı yoktur; orada Kronecker 768 baytlık ultra-düşük belleğiyle üstündür."),

        ("5. İş bölümünü nasıl yaptınız?",
         "Halil yazılım mimarisi, ESP32 donanım testleri ve PQC-Drop ağ protokolünü yürüttü; diğer arkadaşımız teorik ispatlar, olasılık modelleri ve rapor anlatımını üstlendi. Ancak ikimiz de projenin her satırına hakimiz."),

        ("6. ESP32'de hızlanma oldu mu?",
         "Süre olarak okul yöntemiyle yakın çıktı (8.4 ms vs 10.5 ms). Ancak asıl büyük kazancımız bellek oldu: Standart yöntem hafızada 511 katsayılık ara dizi açarken, bizim yöntemimiz ara dizi açmadan 768 baytlık tamponla çalıştı."),

        ("7. Projede Yapay Zekâ kullandınız mı?",
         "Evet, raporumuzda dürüstçe beyan ettik. Kodların testlerini hazırlarken ve grafik çizimlerinde asistan olarak yararlandık; matematiksel hipotez, ispatlar ve donanım testleri tamamen bize aittir."),

        ("8. Model 2 nedir?",
         "Merkezi Limit Teoremi'ne dayanan olasılık formülümüzdür. Deneyi yapmadan önce hangi bit genişliğinde ne kadar hata çıkacağını hesapladık; 200.000 test tam formülümüzün öngördüğü gibi çıktı."),

        ("9. PQC-Drop ne işe yarıyor?",
         "Geliştirdiğimiz matematik motorunu gerçek hayata uyarladığımız bir dosya aktarım aracıdır. Dosyayı AES-256 ile kilitler, anahtarı ise kuantum korumalı Kronecker motorumuzla alıcıya güvenle teslim eder."),

        ("10. Bu proje Türkiye için neden önemli?",
         "Ülkemizin kritik altyapıları, TSK verileri ve bankacılık sistemleri kuantum bilgisayarlar gelmeden önce kuantum sonrası kriptografiye geçmek zorundadır. Yerli ve optimize algoritmalar geliştirmek siber vatan için hayati önem taşır.")
    ]

    for q, a in qa_list:
        qa_card = [
            [Paragraph(f"<b>Soru:</b> {q}", ParagraphStyle('QS', fontName='Roboto-Bold', fontSize=8.2, leading=10.5, textColor=c_blue))],
            [Paragraph(f"<b>Cevap:</b> {a}", ParagraphStyle('AS', fontName='Roboto', fontSize=8.2, leading=11, textColor=c_dark))]
        ]
        t_qa = Table(qa_card, colWidths=[527])
        t_qa.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('LINEBELOW', (0,0), (-1,0), 0.4, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 6))

    # ==================== KISIM 7: 5 DAKİKALIK JÜRİ SUNUM PLANI ====================
    story.append(Paragraph("🎙️ KISIM 7: Jüri Önünde 5 Dakikalık Örnek Sunum Planı", h1_style))
    pitch_data = [
        [Paragraph("Zaman", table_header), Paragraph("Bölüm", table_header), Paragraph("Konuşulacak Kilit Mesaj", table_header)],
        [Paragraph("1. Dakika", table_cell_bold), Paragraph("Giriş & Kuantum Tehlikesi", table_cell_bold), Paragraph("Kuantum bilgisayarların klasik şifreleri kırma riski, 'Şimdi topla sonra çöz' tehlikesi ve NIST'in yeni FIPS 203 standardı.", table_cell)],
        [Paragraph("2. Dakika", table_cell_bold), Paragraph("Matematik & Fikrimiz", table_cell_bold), Paragraph("23² binom açılımından çıkan fikir, Kronecker ikamesi ve katsayıları sıfır etrafında merkezleyerek tamsayıyı 32 bitten 22 bite indirme başarımız (%34 tasarruf).", table_cell)],
        [Paragraph("3. Dakika", table_cell_bold), Paragraph("Teorik İspat & Güvenlik", table_cell_bold), Paragraph("Teorem 1 ispatı, 200.000 testle doğrulanan Model 2 olasılık eğrisi ve 22 bitin altına inildiğinde gizli anahtarın nasıl sızdığı (H4 güvenlik deneyi).", table_cell)],
        [Paragraph("4. Dakika", table_cell_bold), Paragraph("Donanım & Ürün", table_cell_bold), Paragraph("Fiziksel ESP32 çipinde 768 bayt yerel bellekle çalışan C kodumuz ve donanım saat çevrimleri; iki bilgisayar arası dosyayı koruyan PQC-Drop yazılımı.", table_cell)],
        [Paragraph("5. Dakika", table_cell_bold), Paragraph("Sonuç & Kapanış", table_cell_bold), Paragraph("Dürüst bilimsel sonuçlarımız (Büyük sayıda 2x hız, tam KEM'de dönüşüm bedeli), yerli siber güvenlik vizyonu, teşekkür ve jüri sorularına geçiş.", table_cell)]
    ]
    t_pitch = Table(pitch_data, colWidths=[65, 125, 337])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
    ]))
    story.append(t_pitch)
    story.append(Spacer(1, 8))

    # ==================== KISIM 8: PROJE ZİHİN HARİTASI TABLOSU ====================
    story.append(Paragraph("🎯 KISIM 8: Tek Bakışta Proje Zihin Haritası ve Sözlük", h1_style))
    summary_table_data = [
        [Paragraph("Kavram", table_header), Paragraph("Basit 9. Sınıf Açıklaması", table_header), Paragraph("Projedeki Rolü", table_header)],
        [Paragraph("Kuantum Tehdidi", table_cell_bold), Paragraph("Kuantum bilgisayarların bugünkü RSA şifrelerini kırma riski.", table_cell), Paragraph("Neden bu projeyi yaptığımızın gerekçesi.", table_cell)],
        [Paragraph("ML-KEM (FIPS 203)", table_cell_bold), Paragraph("NIST'in kuantuma karşı çıkardığı yeni dünya standardı şifre.", table_cell), Paragraph("Temel aldığımız resmi algoritma.", table_cell)],
        [Paragraph("Kronecker İkamesi", table_cell_bold), Paragraph("Polinom katsayılarını tek bir dev sayıya paketleyip çarpma yöntemi.", table_cell), Paragraph("Polinom çarpımını hızlandırmak için kullandığımız motor.", table_cell)],
        [Paragraph("23² Hilesi", table_cell_bold), Paragraph("Binom katsayılarının elde taşınarak sayıya dönüşmesi.", table_cell), Paragraph("Projenin çıkış noktası ve açma algoritmasının mantığı.", table_cell)],
        [Paragraph("22 Bit Sınırı", table_cell_bold), Paragraph("Katsayıların birbirine taşmaması için gereken en küçük alan.", table_cell), Paragraph("Matematiksel olarak ispatladığımız özgün sınır (Teorem 1).", table_cell)],
        [Paragraph("H4 Güvenlik Deneyi", table_cell_bold), Paragraph("20 bite inilirse gizli anahtarın dışarıya sızması.", table_cell), Paragraph("22 bit sınırının altına inilemeyeceğinin güvenlik kanıtı.", table_cell)],
        [Paragraph("ESP32 Testi", table_cell_bold), Paragraph("Mikrodenetleyici üzerinde C koduyla saat çevrimi ölçümü.", table_cell), Paragraph("768 baytlık mikro bellek modelinin gerçek donanım kanıtı.", table_cell)],
        [Paragraph("PQC-Drop", table_cell_bold), Paragraph("Kuantum korumalı dosya gönderme programı.", table_cell), Paragraph("Teorinin çalışan somut bir ürüne dönüştüğünün kanıtı.", table_cell)]
    ]
    t_sum = Table(summary_table_data, colWidths=[90, 217, 220])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_sum)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Rehber PDF basariyla olusturuldu: {output_path}")

if __name__ == '__main__':
    out_pdf = "/home/halil/Documents/2204a/2204a-pqc-kronecker/docs/TUBITAK_2204A_MASTER_OGRENIM_VE_JURI_REHBERI.pdf"
    create_master_guide(out_pdf)
