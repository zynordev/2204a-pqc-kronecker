#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TÜBİTAK 2204-A Lise Araştırma Projeleri
PQC-Kronecker — 9. Sınıf Seviyesinde Sıfırdan Proje ve Formül Öğrenim Kitabı
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

        if self._pageNumber > 1:
            self.drawString(36, 815, "TÜBİTAK 2204-A — Sıfırdan Mantık ve Formül Öğrenim Kitabı (PQC-Kronecker)")
            self.drawRightString(559, 815, "Halil Erdem Yanık")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 808, 559, 808)

            page_text = f"Sayfa {self._pageNumber} / {page_count}"
            self.drawRightString(559, 25, page_text)
            self.drawString(36, 25, "Kişisel Öğrenim ve Çalışma Rehberi — Formüllerin ve Matematiğin Mantığı")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 35, 559, 35)

        self.restoreState()

def create_guide_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    c_primary = colors.HexColor("#0F172A")    # Koyu gece mavisi
    c_blue = colors.HexColor("#1D4ED8")       # Canlı ana başlık mavisi
    c_teal = colors.HexColor("#0D9488")       # Matematik kutusu rengi
    c_amber = colors.HexColor("#D97706")      # Formül kutusu rengi
    c_red = colors.HexColor("#DC2626")        # Güvenlik açığı rengi
    c_dark = colors.HexColor("#1E293B")       # Okuma metni
    c_bg_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Roboto-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=1,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        fontName='Roboto',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'H1',
        fontName='Roboto-Bold',
        fontSize=12.5,
        leading=16,
        textColor=c_blue,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        fontName='Roboto-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        fontName='Roboto',
        fontSize=8.8,
        leading=12.5,
        textColor=c_dark,
        spaceAfter=5
    )

    math_box_style = ParagraphStyle(
        'MathBox',
        fontName='Roboto',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )

    analogy_style = ParagraphStyle(
        'Analogy',
        fontName='Roboto-Italic',
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#1E1B4B")
    )

    table_header = ParagraphStyle(
        'TH',
        fontName='Roboto-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell_bold = ParagraphStyle(
        'TCB',
        fontName='Roboto-Bold',
        fontSize=8,
        leading=10.5,
        textColor=c_dark
    )

    table_cell = ParagraphStyle(
        'TC',
        fontName='Roboto',
        fontSize=8,
        leading=10.5,
        textColor=c_dark
    )

    story = []

    # ==================== BAŞLIK ====================
    story.append(Spacer(1, 5))
    story.append(Paragraph("TÜBİTAK 2204-A LİSE ARAŞTIRMA PROJELERİ", ParagraphStyle('Tag', fontName='Roboto-Bold', fontSize=9.5, leading=11, textColor=c_teal, alignment=1, spaceAfter=4)))
    story.append(Paragraph("SIFIRDAN PROJE VE FORMÜL ÖĞRENİM KİTABI", title_style))
    story.append(Paragraph("<b>Proje:</b> Kuantum Sonrası Güvenli İletişimde Merkezlenmiş Kronecker İkamesi (ML-KEM)<br/><b>Öğrenci:</b> Halil Erdem Yanık · <b>Amaç:</b> Tüm Matematiksel Formülleri, Sembolleri ve Mantığı 9. Sınıf Düzeyinde Kusursuz Öğrenmek", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_blue, spaceBefore=2, spaceAfter=10))

    # ==================== BÖLÜM 1 ====================
    story.append(Paragraph("📖 BÖLÜM 1: Kriptografinin En Temel Mantığı (Biz Neyi Korumaya Çalışıyoruz?)", h1_style))
    
    sec1 = (
        "<b>1. Simetrik ve Asimetrik Şifreleme Ne Demektir?</b><br/>"
        "• <b>Simetrik Şifreleme (Örnek: AES-256):</b> Tek bir anahtar vardır. Dosyayı aynı anahtarla kilitlersiniz, karşı taraf da aynı anahtarla açar. "
        "Çok hızlıdır (saniyede yüzlerce megabayt kilitler). Ama büyük bir dert vardır: <i>Bu anahtarı karşı tarafa internetten nasıl göndereceksiniz?</i> "
        "Yolda biri anahtarı çalarsa her şeyi açabilir!<br/>"
        "• <b>Asimetrik Şifreleme (Örnek: RSA, ML-KEM):</b> İki ayrı anahtar vardır: <b>Açık Anahtar (Public Key)</b> ve <b>Gizli Anahtar (Private Key)</b>. "
        "Bunu posta kutusu gibi düşünün: Posta kutusunun ağzı herkese açıktır, isteyen mektup atabilir (açık anahtarla şifreler). "
        "Ama kutunun kilidini sadece kutunun sahibi kendi özel anahtarıyla açabilir (gizli anahtar).<br/><br/>"
        "<b>2. KEM (Key Encapsulation Mechanism - Anahtar Kapsülleme) Nedir?</b><br/>"
        "Büyük dosyaları (örneğin 100 MB'lık bir videoyu) yavaş olan asimetrik şifrelemeyle şifreleyemezsiniz. Bu yüzden <b>Hibrit Model</b> kullanılır: "
        "Dosyayı ışık hızında çalışan <b>AES-256</b> kilitler. AES'in 256-bitlik küçük şifresini ise <b>ML-KEM</b> bir zarfın (kapsülün) içine koyar. "
        "KEM işte bu küçük anahtarı zarflama ve zarftan çıkarma işidir."
    )
    story.append(Paragraph(sec1, body_style))
    story.append(Spacer(1, 6))

    # ==================== BÖLÜM 2 ====================
    story.append(Paragraph("📖 BÖLÜM 2: Kuantum Bilgisayar Neyi Kırıyor, Neden Yeni Şifreye Geçiyoruz?", h1_style))
    
    sec2 = (
        "<b>1. Klasik RSA Kilidi Neden Çöküyor?</b><br/>"
        "Bugün bankaların kullandığı RSA kilidinin temeli şudur: Bilgisayara iki tane 300 basamaklı dev asal sayı verirsiniz, bunları saniyede çarpar: "
        "A × B = C. Ancak bir saldırgana sadece devasa 'C' sayısını verip <i>'Hadi bakalım bunun hangi iki asal sayının çarpımı olduğunu bul (çarpanlarına ayır)'</i> "
        "derseniz, dünyadaki tüm süper bilgisayarlar bir araya gelse milyonlarca yıl bulamaz!<br/>"
        "<b>İşte Tehlike:</b> 1994 yılında Peter Shor adında bir matematikçi bir formül buldu (<b>Shor Algoritması</b>). Bu formül normal bilgisayarda çalışmaz "
        "ama bir <b>Kuantum Bilgisayarda</b> çalıştırıldığında o milyonlarca yıl süren çarpanlara ayırma işlemini <b>dakikalar içinde</b> çözer! "
        "Yani kuantum bilgisayar yapıldığı gün bugünkü tüm RSA şifreleri tek tuşla çöp olacaktır.<br/><br/>"
        "<b>2. Kafes Tabanlı Kriptografi (Lattice-Based) ve ML-KEM Nedir?</b><br/>"
        "Bilim insanları düşündü: <i>'Kuantum bilgisayarların bile çözemediği bir matematik problemi var mı?'</i><br/>"
        "Buldular: <b>Kafes Problemleri ve Modül Üzerinde Hatalarla Öğrenme (Module-LWE)</b>.<br/>"
        "Bu yöntem sayıları çarpanlarına ayırmaya değil; çok boyutlu uzayda devasa bir tel örgü (kafes) üzerindeki en yakın noktayı bulma bulmacasına dayanır. "
        "İçine bilerek minik rastgele gürültüler (hatalar) eklenir. Kuantum bilgisayarlar bile bu çok boyutlu kafes bulmacasını çözemez. "
        "NIST, 13 Ağustos 2024'te bu kafes matematiğini kullanan şifrelemeyi <b>FIPS 203 (ML-KEM)</b> adıyla resmi dünya standardı ilan etti."
    )
    story.append(Paragraph(sec2, body_style))
    story.append(Spacer(1, 6))

    # ==================== BÖLÜM 3 ====================
    story.append(Paragraph("📖 BÖLÜM 3: Rapordaki Korkunç Görünen Formüllerin Anlamı", h1_style))
    
    intro_math = "Raporda jürinin gördüğü formüller aslında 9. sınıf seviyesinde çok basit kurallardır. Tek tek tercüme edelim:"
    story.append(Paragraph(intro_math, body_style))

    f1_title = "<b>Formül 1: R_q = Z_q[X] / (X²⁵⁶ + 1),  q = 3329</b>"
    f1_desc = (
        "• <b>X²⁵⁶:</b> Polinomun 256 tane terimi var demektir (yani x⁰, x¹, x² ... x²⁵⁵). Sanki 256 vagonlu bir tren gibi.<br/>"
        "• <b>q = 3329 ve Z_q:</b> Saat matematiğidir (Modüler Aritmetik). Nasıl ki saat 13 olduğunda aslında saat 1 diyorsak (çünkü mod 12'dir); "
        "burada da hiçbir katsayı 3329'u geçemez. Sayı 3329'u geçerse 3329 çıkarılır.<br/>"
        "• <b>X²⁵⁶ + 1 = 0, yani X²⁵⁶ = -1 (Negasiklik İndirgeme):</b> Çarpma yaparken x²⁵⁶ terimi çıkarsa, bunun yerine <b>-1</b> yazarız! "
        "Örnek: x²⁵⁷ terimi çıkarsa bu aslında x²⁵⁶ · x = (-1) · x = <b>-x</b> olur. Yani tren 256 vagondan uzun olamaz, 256'yı aşan vagonlar ters işaretle başa döner!"
    )
    t_f1 = Table([[Paragraph(f1_title, ParagraphStyle('FT1', fontName='Roboto-Bold', fontSize=9, textColor=c_teal)), Paragraph(f1_desc, math_box_style)]], colWidths=[160, 360])
    t_f1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_teal), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t_f1)
    story.append(Spacer(1, 4))

    f2_title = "<b>Formül 2: Merkezlenmiş Gösterim ([-1664, 1664])</b>"
    f2_desc = (
        "Klasik saat gibi düşünün: Sayıları 0 ile 3328 arasında pozitif tutmak yerine, sıfırı ortaya alıyoruz. "
        "3329'un yarısı 1664'tür. Sayı 1664'ten büyükse, örneğin 3328 ise; 3328 - 3329 = <b>-1</b> diyoruz. "
        "Böylece sayılar 0'dan 3328'e kadar devasa pozitif sayılar olmak yerine, sıfırın sağında ve solunda minik sayılar olur: <b>[-1664, +1664]</b>."
    )
    t_f2 = Table([[Paragraph(f2_title, ParagraphStyle('FT2', fontName='Roboto-Bold', fontSize=9, textColor=c_amber)), Paragraph(f2_desc, math_box_style)]], colWidths=[160, 360])
    t_f2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_amber), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t_f2)
    story.append(Spacer(1, 4))

    f3_title = "<b>Formül 3: Gizli Vektör |s| ≤ η ≤ 3</b>"
    f3_desc = (
        "<b>İşte bizim projemizin kalbi burasıdır!</b><br/>"
        "ML-KEM standardında iki polinom çarpılır: Biri internetten gelen açık matris (katsayıları ±1664 olabilir). "
        "Ama diğeri kullanıcının gizli anahtarıdır (s)! Bu gizli anahtarın katsayıları asla büyük sayı olamaz; FIPS 203 kuralı gereği sadece "
        "<b>-3, -2, -1, 0, 1, 2, 3</b> olabilir! Biz bunu fark ettik: Çarpanlardan biri küçücükse, çarpım sonucu da küçük kalır!"
    )
    t_f3 = Table([[Paragraph(f3_title, ParagraphStyle('FT3', fontName='Roboto-Bold', fontSize=9, textColor=c_blue)), Paragraph(f3_desc, math_box_style)]], colWidths=[160, 360])
    t_f3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_blue), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t_f3)
    story.append(Spacer(1, 4))

    f4_title = "<b>Formül 4: Teorem 1 (ℓ_min = 22 Bit)</b>"
    f4_desc = (
        "Jüri bu formülü soracaktır: <i>ℓ_min = ⌊log₂(n · A · η)⌋ + 2</i>. Anlamı şudur:<br/>"
        "• <b>n = 256</b> (polinomda 256 terim var, çarpınca en fazla 256 tane çarpım üst üste biner).<br/>"
        "• <b>A = 1664</b> (bir polinomun en büyük katsayısı).<br/>"
        "• <b>η = 3</b> (gizli anahtarın en büyük katsayısı).<br/>"
        "Hepsini çarpalım: 256 × 1664 × 3 = <b>1.277.952</b>. Çarpım sonucunda bir katsayı en fazla 1 milyon 277 bin olabilir!<br/>"
        "Bilgisayarda bu sayıyı tutmak için kaç bit gerekir? 2²⁰ = 1.048.576 (yetmez, küçük kalır). 2²¹ = 2.097.152 (yeter!). "
        "Bir bit de pozitif/negatif işareti için ekleriz: 21 + 1 = <b>22 BİT!</b> İşte 22 bitin tüm sırrı bu kadar basittir!"
    )
    t_f4 = Table([[Paragraph(f4_title, ParagraphStyle('FT4', fontName='Roboto-Bold', fontSize=9, textColor=c_primary)), Paragraph(f4_desc, math_box_style)]], colWidths=[160, 360])
    t_f4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg_light), ('BOX', (0,0), (-1,-1), 0.8, c_primary), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(t_f4)
    story.append(Spacer(1, 6))

    # ==================== BÖLÜM 4 ====================
    story.append(Paragraph("📖 BÖLÜM 4: Kronecker İkamesi ve 23² Hilesi (Kendi Mantığınız)", h1_style))
    
    sec4 = (
        "<b>Sizin Bulduğunuz 23² Mantığı ile Kronecker Arasındaki Bağ:</b><br/>"
        "Siz dediniz ki: <i>'23² alırken (2x+3)² açarız: 4x² + 12x + 9. Katsayılar 4, 12, 9'dur. Sağdan sola elde taşırız: 9 kalır, 12'nin 2'si kalır 1 sola taşar, 4+1=5 olur. Cevap 529.'</i><br/><br/>"
        "Kronecker ikamesi tam olarak bu işlemin <b>ters yönde çalışan ikiz kardeşidir</b>:<br/>"
        "1. Elimizde 256 terimli harfli bir polinom var: c₀ + c₁X + c₂X² + ... + c₂₅₅X²⁵⁵.<br/>"
        "2. Biz X yerine <b>2²²</b> (yani kutucuk genişliği olarak 22 bit) koyuyoruz.<br/>"
        "3. Polinom tek bir devasa sayıya dönüşüyor (256 × 22 = <b>5632 bitlik dev bir sayı</b>).<br/>"
        "4. Bilgisayar bu iki dev sayıyı normal ilkokul çarpması gibi tek vuruşta çarpıyor.<br/>"
        "5. Sonuçtaki dev sayıdan katsayıları geri okurken, tıpkı sizin yaptığınız gibi sağdan sola 22-bitlik blokları kesiyoruz. "
        "Eğer katsayı eksi çıkarsa bir üst bloktan <b>ödünç (borrow)</b> alıyoruz.<br/>"
        "<b>Standart Kronecker'den Farkımız:</b> Standart yöntem katsayıları pozitif aldığı için kutucukları 32 bit açıyordu ve sayı <b>8192 bit</b> oluyordu. "
        "Biz gizli anahtarın 3'ü geçmediğini bildiğimiz için kutucukları 22 bite indirdik ve <b>%34 hafıza tasarrufu</b> sağladık!"
    )
    story.append(Paragraph(sec4, body_style))
    story.append(Spacer(1, 6))

    # ==================== BÖLÜM 5 ====================
    story.append(Paragraph("📖 BÖLÜM 5: Güvenlik Açığı Deneyi (H4) — Neden 20 Bit Yapamayız?", h1_style))
    
    sec5 = (
        "Biri çıkıp diyebilir ki: <i>'Madem 22 bit yaptınız, gelin bunu 20 bit yapalım, daha da küçülsün, daha az yer kaplasın.'</i><br/>"
        "İşte projenin en havalı bilimsel keşfi buradadır:<br/>"
        "Kutucukları 20 bit yaparsanız, normal rastgele sayılarda sistem çalışır gibi görünür (taşma nadiren olur). "
        "<b>AMA bir hacker (saldırgan) bunu fark ederse ne yapar?</b><br/>"
        "Saldırgan özel olarak tasarlanmış tuzak bir şifreli metin yollar (katsayıları hep +1664 ve -1664 olan aşırı uç bir polinom). "
        "Bu tuzak polinom çarpıldığında sonuç 20 bitlik kutucuğa sığmaz ve <b>TAŞAR (overflow)</b>. Taşma olunca şifre çözme işlemi hata verir.<br/>"
        "<b>Büyük Sır:</b> Hatanın çıkıp çıkmaması tamamen kurbanın gizli anahtarındaki katsayıların mutlak toplamına (<b>||s||₁ normuna</b>) bağlıdır! "
        "Saldırgan ekranda hata çıkıp çıkmadığına bakarak kurbanın gizli anahtarının büyük mü küçük mü olduğunu anlar ve gizli anahtarı adım adım çalar! "
        "Yani 22 bit sadece bir matematik kuralı değil; <b>aşılırsa şifrenin kırıldığı kırmızı güvenlik çizgisidir!</b>"
    )
    story.append(Paragraph(sec5, body_style))
    story.append(Spacer(1, 6))

    # ==================== BÖLÜM 6 ====================
    story.append(Paragraph("📖 BÖLÜM 6: Donanım Testi (ESP32) — Çipte Neden Bu Kadar Önemli?", h1_style))
    
    sec6 = (
        "<b>1. Bilgisayar ile ESP32 Arasındaki Fark Nedir?</b><br/>"
        "Laptopunuzda 16 GB RAM ve 8 çekirdekli dev işlemci vardır; orada hafıza bitmez. "
        "Ama akıllı prizlerde, güvenlik kameralarında veya dronelarda kullanılan <b>ESP32 çipinde sadece 512 KB RAM</b> vardır! Hafıza çok kıymetlidir.<br/><br/>"
        "<b>2. Standart Okul Yöntemi vs. Bizim 24-bit Comba Yöntemimiz:</b><br/>"
        "• <b>Standart Okul Çarpması:</b> İki polinomu çarparken aradaki çarpımları saklamak için hafızada 511 katsayılık kocaman ara diziler açmak zorundadır. Hafızayı şişirir.<br/>"
        "• <b>Bizim Yöntemimiz (24-bit Comba):</b> Biz ara dizi açmayız! Katsayıları tek tek çarpıp anında bir kumbara gibi akümülatörde toplarız. "
        "Her katsayı 24 bit (tam 3 bayt) olduğu için 256 katsayı hafızada 256 × 3 = <b>tam 768 bayt</b> yer kaplar!<br/>"
        "<b>3. Gerçek Çipte Ne Ölçtük?</b><br/>"
        "ESP32'ye kodu yükledik, işlemcinin içindeki donanım saat sayacını okuduk:<br/>"
        "• Standart Okul Yöntemi: <b>677.956 saat çevrimi</b> sürdü.<br/>"
        "• Bizim Yöntemimiz: <b>841.234 saat çevrimi</b> sürdü.<br/>"
        "İki yöntem de <b>%100 birebir aynı katsayıları</b> üretti! Süre olarak okul yöntemi biraz daha hızlı olsa da, "
        "bizim yöntemimiz ara hafıza tamponunu sıfırlayarak <b>768 baytlık ultra-düşük RAM sınırında</b> çalışmayı başardı!"
    )
    story.append(Paragraph(sec6, body_style))
    story.append(Spacer(1, 6))

    # ==================== BÖLÜM 7 ====================
    story.append(Paragraph("📖 BÖLÜM 7: PQC-Drop Nedir? (Yazılım Tarafı)", h1_style))
    
    sec7 = (
        "TÜBİTAK jürisi sadece formül ve konsol çıktısı görmek istemez; <i>'Bu yaptığınız nerede işe yarayacak?'</i> diye sorar.<br/>"
        "İşte cevabımız: <b>PQC-Drop</b>.<br/>"
        "PQC-Drop, AirDrop gibi iki bilgisayar arasında dosya gönderen bir yazılımdır:<br/>"
        "1. Alıcı bilgisayar ML-KEM açık anahtarını üretir.<br/>"
        "2. Gönderici bilgisayar dosyayı kilitleyecek olan 256-bitlik AES anahtarını bizim <b>Kronecker motorumuzla</b> kapsüller.<br/>"
        "3. Dosya internetten veya yerel ağdan şifreli akar.<br/>"
        "4. Alıcı anahtarı çözüp dosyayı kurtarır.<br/>"
        "Yolda ağ trafiğini dinleyen bir casus (Wireshark ile test ettik), paketin içindeki dosyayı veya anahtarı kuantum bilgisayarla bile asla göremez!"
    )
    story.append(Paragraph(sec7, body_style))
    story.append(Spacer(1, 8))

    # ==================== BÖLÜM 8 ====================
    story.append(Paragraph("🎯 BÖLÜM 8: Özet Zihin Haritası (Tek Bakışta Tüm Proje)", h1_style))

    summary_table_data = [
        [Paragraph("Kavram", table_header), Paragraph("Basit Açıklaması", table_header), Paragraph("Projedeki Rolü", table_header)],
        [Paragraph("Kuantum Tehdidi", table_cell_bold), Paragraph("Kuantum bilgisayarların bugünkü RSA şifrelerini kırma riski.", table_cell), Paragraph("Neden bu projeyi yaptığımızın gerekçesi.", table_cell)],
        [Paragraph("ML-KEM (FIPS 203)", table_cell_bold), Paragraph("NIST'in kuantuma karşı çıkardığı yeni dünya standardı şifre.", table_cell), Paragraph("Temel aldığımız resmi algoritma.", table_cell)],
        [Paragraph("Kronecker İkamesi", table_cell_bold), Paragraph("Polinom katsayılarını tek bir dev sayıya paketleyip çarpma yöntemi.", table_cell), Paragraph("Polinom çarpımını hızlandırmak için kullandığımız motor.", table_cell)],
        [Paragraph("23² Hilesi", table_cell_bold), Paragraph("Binom katsayılarının elde taşınarak sayıya dönüşmesi.", table_cell), Paragraph("Projenin çıkış noktası ve açma algoritmasının mantığı.", table_cell)],
        [Paragraph("22 Bit Sınırı", table_cell_bold), Paragraph("Katsayıların birbirine taşmaması için gereken en küçük alan.", table_cell), Paragraph("Matematiksel olarak ispatladığımız özgün sınır (Teorem 1).", table_cell)],
        [Paragraph("H4 Güvenlik Deneyi", table_cell_bold), Paragraph("20 bite inilirse gizli anahtarın dışarıya sızması.", table_cell), Paragraph("22 bit sınırının altına inilemeyeceğinin güvenlik kanıtı.", table_cell)],
        [Paragraph("ESP32 Testi", table_cell_bold), Paragraph("Mikrodenetleyici üzerinde C koduyla saat çevrimi ölçümü.", table_cell), Paragraph("768 baytlık mikro bellek modelinin gerçek donanım kanıtı.", table_cell)],
        [Paragraph("PQC-Drop", table_cell_bold), Paragraph("Kuantum korumalı dosya gönderme programı.", table_cell), Paragraph("Teorinin çalışan somut bir ürüne dönüştüğünün kanıtı.", table_cell)]
    ]

    t_sum = Table(summary_table_data, colWidths=[90, 215, 215])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sum)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Kitapcik basariyla olusturuldu: {output_path}")

if __name__ == '__main__':
    out_pdf = "/home/halil/Documents/2204a/2204a-pqc-kronecker/docs/PROJE_VE_FORMUL_OGRENIM_KITABI_2204A.pdf"
    create_guide_pdf(out_pdf)
