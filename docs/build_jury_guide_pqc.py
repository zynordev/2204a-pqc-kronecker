#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması
Kuantum Sonrası Kriptografide Merkezlenmiş Kronecker İkamesi (ML-KEM)
9. Sınıf Seviyesinde Jüri Savunma, Metodoloji ve Öğrenim Rehberi PDF Oluşturucu
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Fontları kaydet (Türkçe karakter destekli Roboto)
pdfmetrics.registerFont(TTFont('Roboto', '/usr/share/fonts/TTF/Roboto-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-Bold', '/usr/share/fonts/TTF/Roboto-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-Italic', '/usr/share/fonts/TTF/Roboto-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-BoldItalic', '/usr/share/fonts/TTF/Roboto-BoldItalic.ttf'))

# Sayfa Numaralandırıcı
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
        self.setFillColor(colors.HexColor("#4A5568"))

        # Kapak sayfası hariç üst ve alt bilgi
        if self._pageNumber > 1:
            # Header
            self.drawString(40, 815, "TÜBİTAK 2204-A Lise Araştırma Projeleri — Jüri Savunma ve Öğrenim Rehberi")
            self.drawRightString(555, 815, "PQC-Kronecker (ML-KEM)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(40, 808, 555, 808)

            # Footer
            page_text = f"Sayfa {self._pageNumber} / {page_count}"
            self.drawRightString(555, 25, page_text)
            self.drawString(40, 25, "Gizli & Proje Çalışma Dokümanı — 9. Sınıf Düzeyi Anlatım")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(40, 35, 555, 35)

        self.restoreState()


def create_pqc_jury_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Özel Tipografi Stilleri
    c_primary = colors.HexColor("#0F172A")    # Çok Koyu Lacivert / Siyah
    c_blue = colors.HexColor("#1E40AF")       # Güçlü Mavi
    c_accent = colors.HexColor("#0369A1")     # Canlı Mavi
    c_dark = colors.HexColor("#1E293B")       # Gövde Metni
    c_bg_box = colors.HexColor("#F8FAFC")     # Açık Kutu Arka Planı
    c_border = colors.HexColor("#E2E8F0")     # Çerçeve Rengi
    c_success = colors.HexColor("#047857")    # Yeşil Vurgu
    c_warn = colors.HexColor("#B45309")       # Turuncu Vurgu

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Roboto-Bold',
        fontSize=21,
        leading=25,
        textColor=c_primary,
        alignment=1,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        fontName='Roboto',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Roboto-Bold',
        fontSize=13.5,
        leading=17,
        textColor=c_blue,
        spaceBefore=12,
        spaceAfter=7,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Roboto-Bold',
        fontSize=11,
        leading=14,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Roboto',
        fontSize=9,
        leading=12.5,
        textColor=c_dark,
        spaceAfter=5
    )

    bold_body_style = ParagraphStyle(
        'BoldBody_Custom',
        fontName='Roboto-Bold',
        fontSize=9,
        leading=12.5,
        textColor=c_dark,
        spaceAfter=5
    )

    quote_style = ParagraphStyle(
        'Quote_Custom',
        fontName='Roboto-Italic',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A")
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        fontName='Roboto',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Roboto',
        fontSize=8,
        leading=10.5,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Roboto-Bold',
        fontSize=8,
        leading=10.5,
        textColor=c_dark
    )

    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        fontName='Roboto-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    story = []

    # ==================== KAPAK & BAŞLIK ====================
    story.append(Spacer(1, 10))
    story.append(Paragraph("TÜBİTAK 2204-A LİSE ARAŞTIRMA PROJELERİ", ParagraphStyle('TopTag', fontName='Roboto-Bold', fontSize=10, leading=12, textColor=c_accent, alignment=1, spaceAfter=4)))
    story.append(Paragraph("Jüri Savunma ve Öğrenim Rehberi", title_style))
    story.append(Paragraph("<b>Proje Adı:</b> Kuantum Sonrası Güvenli İletişimde Merkezlenmiş Kronecker İkamesi ile Polinom Çarpımı (NIST FIPS 203 ML-KEM)<br/><b>Öğrenci:</b> Halil Erdem Yanık · <b>Alan:</b> Bilgisayar (Yazılım / Siber Güvenlik) · <b>Hedef:</b> 9. Sınıf Düzeyinde Kusursuz Hakimiyet", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_blue, spaceBefore=4, spaceAfter=14))

    # ==================== 1. ASANSÖR KONUŞMASI ====================
    story.append(Paragraph("🎯 1. 30 Saniyelik Asansör Konuşması (Jüriye İlk Giriş)", h1_style))
    
    elevator_text = (
        "<b>\"Değerli jüri üyeleri;</b> bugün bankacılık ve internette kullandığımız klasik şifreler (RSA), "
        "gelecekteki güçlü bir kuantum bilgisayarla dakikalar içinde kırılabilecektir. NIST bu tehdide karşı "
        "Ağustos 2024'te kuantum korumalı dünya standardı <b>ML-KEM</b>'i yayımladı.<br/><br/>"
        "Ancak ML-KEM'in kalbinde bilgisayarları çok yoran 256 terimli polinom çarpımları vardır. "
        "Biz bu projede, polinom katsayılarını tek bir büyük sayıya paketleyip tek vuruşta çarpan "
        "<b>Kronecker ikamesini</b> inceledik. Katsayıları sıfır etrafında merkezleyerek gereken tamsayı boyutunu "
        "<b>32 bitten 22 bite indirdik (%34 tasarruf)</b>. Bu sınırın altına inildiğinde gizli anahtarın nasıl sızdığını ispatladık. "
        "Yöntemimizi iki bilgisayar arası güvenli dosya aktarımı yapan <b>PQC-Drop</b> yazılımında ve fiziksel bir "
        "<b>ESP32 mikrodenetleyicisi</b> üzerinde donanım saat çevrimleriyle başarıyla test ettik.\""
    )
    
    t_box = Table([[Paragraph(elevator_text, quote_style)]], colWidths=[520])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#93C5FD")),
        ('PADDING', (0,0), (-1,-1), 9),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 12))

    # ==================== 2. 9. SINIF SEVİYESİNDE TEMEL MANTIK ====================
    story.append(Paragraph("🧠 2. 9. Sınıf Seviyesinde Temel Mantık: Ne Yaptık?", h1_style))

    p1 = (
        "<b>A. Kuantum Tehdidi ve 'Şimdi Topla, Sonra Çöz' (Y2Q):</b><br/>"
        "Şu an telefonlarımız ve bankalar verileri RSA ile şifreler. RSA, çok büyük iki asal sayının çarpımını "
        "çarpanlarına ayırmanın klasik bilgisayarlar için binlerce yıl sürmesine güvenir. Ancak kuantum bilgisayarlar "
        "(Shor algoritmasıyla) bu işlemi dakikalar içinde çözebilir. Saldırganlar bugün internetteki şifreli askeri ve kişisel "
        "verileri kaydedip depolamaktadır (<i>Harvest Now, Decrypt Later</i>). Amaçları kuantum bilgisayar çıktığında bu arşivleri açmaktır. "
        "Bu yüzden kuantum korumalı şifrelemeye (PQC) <b>hemen bugün</b> geçmek zorundayız."
    )
    story.append(Paragraph(p1, body_style))

    p2 = (
        "<b>B. Çıkış Noktamız: İki Basamaklı Sayının Karesi Hilesi (23²):</b><br/>"
        "8. sınıf cebir bilgisini hatırlayalım: (2x + 3)² = 4x² + 12x + 9.<br/>"
        "• 9 birler basamağında kalır.<br/>"
        "• 12'nin 2'si kalır, 1 onlar basamağına elde olarak taşınır: 4 + 1 = 5.<br/>"
        "• Basamakları birleştirince: <b>529</b> çıkar! Gerçekten de 23² = 529'dur.<br/>"
        "<b>Büyük Fikir:</b> Sayılar polinom gibi, polinomlar da sayılar gibi davranır! Katsayılar sağdan sola elde taşıma "
        "(carry) mekanizmasıyla sayılara bağlanır. Bilgisayarlar harfli cebirle uğraşmayı sevmez ama büyük sayıları çarpmakta çok hızlıdır."
    )
    story.append(Paragraph(p2, body_style))

    p3 = (
        "<b>C. Kronecker İkamesi Nedir?</b><br/>"
        "Polinomun x değişkeni yerine 2'nin bir kuvvetini (örneğin 2²²) koyarız. Böylece 256 terimli harfli polinom, "
        "tek bir devasa tamsayıya dönüşür. Bilgisayarın işlemcisi iki dev sayıyı tek bir çarpma işlemiyle çarpar. "
        "Ardından bu dev sayıyı 22-bitlik bloklar halinde dilimleyerek çarpım polinomunun katsayılarını geri okuruz."
    )
    story.append(Paragraph(p3, body_style))

    p4 = (
        "<b>D. Bizim Özgün Buluşumuz: Neden 32 Bit Değil de 22 Bit?</b><br/>"
        "• <b>Klasik Yöntem (İşaretsiz):</b> Katsayıları pozitif [0, 3328] kabul eder. Katsayılar çarpılınca birbirine taşmasın "
        "diye blok başına 32 bit ayırır. Bu da <b>8192 bitlik</b> devasa bir sayı üretir.<br/>"
        "• <b>Bizim Yöntemimiz (Merkezlenmiş / İşaretli):</b> ML-KEM'de gizli anahtarın katsayıları daima [-3, +3] gibi çok küçüktür! "
        "Biz katsayıları sıfır etrafında merkezledik: [-1664, +1664]. En büyük katsayı çarpımı 2200 kat küçüldü! "
        "Böylece blok genişliğini <b>32 bitten 22 bite</b>, toplam sayıyı <b>8192 bitten 5632 bite indirdik (%34 tasarruf)</b>."
    )
    story.append(Paragraph(p4, body_style))
    story.append(Spacer(1, 10))

    # ==================== 3. 5 BÜYÜK BİLİMSEL KANIT ====================
    story.append(Paragraph("🔬 3. Jüriyi Büyüleyecek 5 Büyük Bilimsel Kanıtımız", h1_style))

    k1 = (
        "<b>1. Kanıt: Matematiksel Taşma Sınırı İspatı (ℓ_min = 22):</b><br/>"
        "Jüri 'Neden 22 bit?' dediğinde tahtaya formülümüzü yazarız: 256 terim × 1664 × 3 = 1.277.952. "
        "Bu sayıyı işaret bitiyle güvenle saklamak için <b>en az 22 bit</b> şarttır. 200.000 rastgele denemeyle formülün %100 kusursuz çalıştığını kanıtladık."
    )
    story.append(Paragraph(k1, body_style))

    k2 = (
        "<b>2. Kanıt: Güvenlik Açığı Deneyi (H4 Deneyi — En Büyük Kozumuz!):</b><br/>"
        "Jüri '20 bit yapsak daha çok tasarruf etmez miyiz?' diye sorarsa: <i>'Hafızadan tasarruf ederiz ama güvenlik çöker!'</i> deriz. "
        "Çünkü 20 bite inilirse katsayılar taşar ve hata üretir. Hatanın çıkıp çıkmaması kurbanın <b>gizli anahtarının büyüklüğüne (||s||₁)</b> "
        "bağlı hale gelir. Saldırgan hata sinyallerine bakarak gizli anahtarı sızdırabilir! 22 bit altına inilemeyeceğini ilk kez güvenlikle ispatladık."
    )
    story.append(Paragraph(k2, body_style))

    k3 = (
        "<b>3. Kanıt: Hız Karşılaştırması ve Bilimsel Dürüstlük:</b><br/>"
        "Büyük tamsayı çarpımında 22-bit paketleme standart 32-bite göre <b>2,05 kat daha hızlıdır</b>. "
        "Ancak uçtan uca tüm ML-KEM sürecinde NIST'in resmi NTT yöntemi daha hızlı kalmıştır. Çünkü sayıları paketleyip geri açmak ek süre alır. "
        "Jüriye dürüstçe söyledik: <i>'Kronecker her yerde değil; NTT donanımı olmayan IoT ve akıllı kartlarda üstündür.'</i>"
    )
    story.append(Paragraph(k3, body_style))

    k4 = (
        "<b>4. Kanıt: PQC-Drop (Çalışan Güvenli Dosya Aktarımı):</b><br/>"
        "Projeyi teoride bırakmadık. İki bilgisayar arasında çalışan <b>PQC-Drop</b> adında bir yazılım geliştirdik. "
        "Dosyayı AES-256-GCM ile kilitlerken, oturum anahtarını bizim Kronecker motorumuz kuantum korumalı olarak iletti. "
        "Wireshark ile PCAP ağ paketlerini dinleyerek kuantum güvenliğini şeffafça doğruladık."
    )
    story.append(Paragraph(k4, body_style))

    k5 = (
        "<b>5. Kanıt: Gerçek Mikrodenetleyici (ESP32) Donanım Doğrulaması:</b><br/>"
        "Simülasyonda kalmadık; 24-bit Comba katsayı akümülatörünü C/C++ ile fiziksel bir <b>ESP32 çipine</b> flashladık. "
        "Doğrudan çipin donanım register'ı (<code>esp_cpu_get_cycle_count()</code>) ile 100 bağımsız test yaptık. "
        "Okul yöntemiyle %100 birebir aynı katsayıları ürettik ve ara dizileri sıfırlayarak <b>768 baytlık mikro bellek sınırında</b> çalıştığını kanıtladık!"
    )
    story.append(Paragraph(k5, body_style))
    story.append(Spacer(1, 10))

    # ==================== ESP32 TABLOSU ====================
    story.append(Paragraph("📊 Gerçek ESP32 Donanım Ölçüm Sonuçlarımız (80 MHz, N=256, q=3329)", h2_style))
    
    esp_data = [
        [Paragraph("Yöntem", table_cell_header), Paragraph("Ortalama Saat Çevrimi", table_cell_header), Paragraph("Ortalama Süre", table_cell_header), Paragraph("Doğruluk", table_cell_header), Paragraph("Yerel Bellek", table_cell_header)],
        [Paragraph("1. Standart Okul Yöntemi", table_cell_bold), Paragraph("677.956 çevrim", table_cell), Paragraph("8.473 µs", table_cell), Paragraph("%100 Eşleşme", table_cell), Paragraph("256 katsayı ara dizi", table_cell)],
        [Paragraph("2. Merkezlenmiş Kronecker / Comba", table_cell_bold), Paragraph("841.234 çevrim", table_cell), Paragraph("10.514 µs", table_cell), Paragraph("%100 Eşleşme", table_cell), Paragraph("<b>768 Bayt (Ara tamponsuz)</b>", table_cell)]
    ]
    t_esp = Table(esp_data, colWidths=[130, 105, 85, 80, 120])
    t_esp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,1), (3,-1), 'CENTER'),
    ]))
    story.append(t_esp)
    story.append(Spacer(1, 14))

    # ==================== 4. EN KRİTİK 10 JÜRİ SORUSU ====================
    story.append(Paragraph("❓ 4. En Kritik 10 Jüri Sorusu ve 9. Sınıf Cevapları", h1_style))

    qa_list = [
        ("1. Yeni bir şifreleme algoritması mı buldunuz?",
         "Hayır jüri üyem. Yeni bir şifreleme icat etmedik; NIST'in resmi standardı olan FIPS 203'ü (ML-KEM) temel aldık. Standardın kalbindeki en ağır işlem olan 256 terimli polinom çarpımını optimize ettik."),

        ("2. Kronecker ikamesini ilk siz mi buldunuz?",
         "Hayır, Leopold Kronecker 1882'de buldu. Ancak ML-KEM standardında katsayıları sıfır etrafında merkezleyerek 32 bitten 22 bite indiren ve ESP32'de 768 bayt yerel bellek modelini kuran dünyada ilk biziz."),

        ("3. Neden 22 bit? 20 bit yapsak hafızadan daha çok tasarruf etmez miyiz?",
         "Tasarruf ederiz ama güvenlik çöker! 20 bit yaparsak katsayılar taşar ve hata üretir. Bu hata kurbanın gizli anahtarının büyüklüğüne bağlı olduğu için saldırgan gizli anahtarı adım adım tahmin edebilir (H4 deneyimizle bunu kanıtladık)."),

        ("4. NTT varken Kronecker'e ne gerek var?",
         "NTT çok hızlıdır ama çalışması için özel matematiksel asal sayılar ve yüksek RAM gerekir. Küçük IoT çiplerinde veya akıllı kartlarda NTT donanımı yoktur; orada Kronecker büyük bellek avantajı sağlar."),

        ("5. Kendi aranızda iş bölümünü nasıl yaptınız?",
         "Halil yazılım mimarisi, ESP32 donanım testleri ve PQC-Drop ağ protokolünü yürüttü; diğer arkadaşımız teorik ispatlar, olasılık modelleri ve rapor anlatımını üstlendi. Ancak ikimiz de projenin her satırını savunabiliriz."),

        ("6. ESP32'de hızlanma oldu mu?",
         "Süre olarak okul yöntemiyle yakın çıktı (0.81x). Ancak asıl büyük kazancımız bellek oldu: Standart yöntem 511 katsayılık ara dizi açarken, bizim yöntemimiz 768 baytlık tamponla RAM'i hiç şişirmeden çalıştı."),

        ("7. Projede Yapay Zekâ kullandınız mı?",
         "Evet, raporumuzda da dürüstçe beyan ettik. Kodların testlerini hazırlarken ve grafik çizimlerinde asistan olarak kullandık; matematiksel hipotez, ispatlar ve donanım testleri tamamen bize aittir."),

        ("8. Model 2 nedir?",
         "Merkezi Limit Teoremi'ne dayanan olasılık formülümüzdür. Deneyi yapmadan önce hangi bit genişliğinde ne kadar hata çıkacağını önceden hesapladık; 200.000 test tam formülümüzün öngördüğü gibi çıktı."),

        ("9. PQC-Drop ne işe yarıyor?",
         "Geliştirdiğimiz matematik motorunu gerçek hayata uyarladığımız bir dosya aktarım aracıdır. Dosyayı AES-256 ile şifreler, anahtarı ise kuantum korumalı Kronecker motorumuzla alıcıya güvenle teslim eder."),

        ("10. Bu proje Türkiye için neden önemli?",
         "Ülkemizin kritik altyapıları, TSK verileri ve bankacılık sistemleri kuantum bilgisayarlar gelmeden önce kuantum sonrası kriptografiye geçmek zorundadır. Yerli ve optimize algoritmalar geliştirmek siber vatan güvenliğimiz için hayati önem taşır.")
    ]

    for q, a in qa_list:
        qa_card = [
            [Paragraph(f"<b>Soru:</b> {q}", ParagraphStyle('QStyle', fontName='Roboto-Bold', fontSize=8.5, leading=11, textColor=c_blue))],
            [Paragraph(f"<b>Cevap:</b> {a}", ParagraphStyle('AStyle', fontName='Roboto', fontSize=8.5, leading=11.5, textColor=c_dark))]
        ]
        t_qa = Table(qa_card, colWidths=[520])
        t_qa.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_bg_box),
            ('BOX', (0,0), (-1,-1), 0.6, c_border),
            ('LINEBELOW', (0,0), (-1,0), 0.4, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))

    # ==================== 5. 5 DAKİKALIK JÜRİ SUNUM PLANI ====================
    story.append(Paragraph("🎙️ 5. Jüri Önünde 5 Dakikalık Örnek Sunum Planı", h1_style))

    pitch_data = [
        [Paragraph("Zaman", table_cell_header), Paragraph("Bölüm", table_cell_header), Paragraph("Konuşulacak Kilit Mesaj", table_cell_header)],
        [Paragraph("1. Dakika", table_cell_bold), Paragraph("Giriş & Kuantum Tehlikesi", table_cell_bold), Paragraph("Kuantum bilgisayarların klasik şifreleri kırma riski, 'Şimdi topla sonra çöz' tehlikesi ve NIST'in yeni FIPS 203 ML-KEM standardı.", table_cell)],
        [Paragraph("2. Dakika", table_cell_bold), Paragraph("Matematik & Fikrimiz", table_cell_bold), Paragraph("23² binom açılımından çıkan fikir, Kronecker ikamesi ve katsayıları sıfır etrafında merkezleyerek tamsayıyı 32 bitten 22 bite indirme başarımız (%34 tasarruf).", table_cell)],
        [Paragraph("3. Dakika", table_cell_bold), Paragraph("Teorik İspat & Güvenlik", table_cell_bold), Paragraph("Teorem 1 ispatı, 200.000 testle doğrulanan Model 2 olasılık eğrisi ve 22 bitin altına inildiğinde gizli anahtarın nasıl sızdığı (H4 güvenlik deneyi).", table_cell)],
        [Paragraph("4. Dakika", table_cell_bold), Paragraph("Donanım & Ürün", table_cell_bold), Paragraph("Fiziksel ESP32 çipinde 768 bayt yerel bellekle çalışan C kodumuz ve donanım saat çevrimleri; iki bilgisayar arası dosyayı koruyan PQC-Drop yazılımı.", table_cell)],
        [Paragraph("5. Dakika", table_cell_bold), Paragraph("Sonuç & Kapanış", table_cell_bold), Paragraph("Dürüst bilimsel sonuçlarımız (Büyük sayıda 2x hız, tam KEM'de dönüşüm bedeli), yerli siber güvenlik vizyonu, teşekkür ve jüri sorularına geçiş.", table_cell)]
    ]
    t_pitch = Table(pitch_data, colWidths=[65, 125, 330])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
    ]))
    story.append(t_pitch)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF basariyla olusturuldu: {output_path}")

if __name__ == '__main__':
    out_pdf = "/home/halil/Documents/2204a/2204a-pqc-kronecker/docs/JURI_SAVUNMA_VE_OGRENIM_REHBERI_2204A.pdf"
    create_pqc_jury_pdf(out_pdf)
