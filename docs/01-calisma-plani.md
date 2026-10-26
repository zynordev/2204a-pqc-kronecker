# 01 — Çalışma Planı

*Son güncelleme: 2026-10-26. Kesin başvuru tarihi Aşama 0'da şartnameden doğrulanıp tablo güncellenecek.*

## Ekip ve rol dağılımı

| Kişi | Ana sorumluluk | Yan sorumluluk |
|---|---|---|
| Öğrenci A (Halil) | Yazılım, deney altyapısı, kod okuma/analiz | Performans deneyleri, prototip |
| Öğrenci B | Teori: ispatlar, olasılık modeli, literatür | Rapor dili, grafiklerin yorumu |
| Danışman öğretmen | Aşama kapanış onayı, rapor okuma | Şartname uyumu |

Kural: **iki öğrenci de her şeyi anlatabilmeli.** Her aşama sonunda karşılıklı "bana anlat" oturumu yapılır
(A teoriyi, B kodu anlatır).

## Aşamalar

Her aşamanın bir **çıkış kriteri** var. Kriter sağlanmadan sonraki aşamaya geçilmez
(bkz. [05 — Hata kontrolü](05-hata-kontrol.md)).

### Aşama 0 — Kurulum (26 Eki – 1 Kas 2026)
- [x] Repo iskeleti, dokümanlar, CI
- [x] Ön ölçüm betiği arşivlendi ([experiments/00-on-olcum](../experiments/00-on-olcum/sonuc.md))
- [ ] 2204-A güncel şartnamesini oku: son tarih, sayfa sınırı, rapor şablonu, YZ kullanım kuralı
- [ ] Danışmanla toplantı: plan + [06 — Açık sorular](06-acik-sorular.md)
- **Çıkış:** dokümanlar push'lu; şartname maddeleri 06'ya işlendi; danışman planı gördü.

### Aşama 1 — Literatür ve teori (2 – 15 Kas)
- [ ] [02](02-literatur.md)'deki her kaynağı bul, oku, künyesini doğrula (✘ → ✔)
- [ ] FIPS 203'ün ilgili bölümlerini oku: parametreler, CBD, NTT, K-PKE
- [ ] Taşma lemmasının ispatını elle yaz ([04](04-teori.md)), keskinlik örneğini elle hesapla
- [ ] Olasılık modelini (normal yaklaşım) kur
- [ ] Kategori kararı (Matematik / Bilgisayar)
- **Çıkış:** iki öğrenci de ispatı tahtada anlatıyor; 02 tablosunda ✘ kalmadı; kategori yazıldı.

### Aşama 2 — Referans ML-KEM (16 – 29 Kas)
- [ ] Saf Python ML-KEM-512/768/1024: SHAKE, CBD, NTT, K-PKE, KEM (FIPS 203 algoritma numaralarıyla)
- [ ] NIST ACVP test vektörleri ile test (keyGen, encaps, decaps)
- [ ] Okul yöntemi (schoolbook) negasiklik çarpım = altın standart
- **Çıkış:** tüm resmî test vektörleri geçiyor; CI yeşil.

### Aşama 3 — Kronecker motorları (30 Kas – 13 Ara)
- [ ] Varyantlar: işaretsiz 32 bit · işaretli 22 bit · ofset hileli · mod 2^(nℓ)+1 negasiklik ·
      modül toplamını paketli alanda yapan
- [ ] Her varyant ML-KEM'e takılabilir (çarpım fonksiyonu parametre)
- [ ] Her varyant: schoolbook'a karşı 10.000 rastgele + kenar durum testi; ML-KEM test vektörleri hâlâ geçiyor
- **Çıkış:** H1 doğrulandı.

### Aşama 4 — Deneyler (14 Ara 2026 – 3 Oca 2027)
- [ ] H2: teorik eşik vs ölçülen eşik; olasılık modeli vs ölçülen hata oranı (grafik)
- [ ] H3: performans (tek çarpım + tam keygen/encaps/decaps), ≥1000 tekrar, medyan + çeyrekler arası aralık
- [ ] H4: dar ℓ ile gizli anahtara bağlı hata gösterimi
- **Çıkış:** her deney klasöründe betik + ham CSV + grafik + sonuc.md; betik tek komutla yeniden üretiyor.

### Aşama 5 — PQC-Drop prototipi (4 – 17 Oca)
- [ ] CLI: `pqcdrop alici` / `pqcdrop gonder dosya ip`
- [ ] El sıkışma: ML-KEM (bizim Kronecker motorumuzla) → HKDF → AES-256-GCM parça parça akış
- [ ] Bütünlük: alınan dosyanın SHA-256'sı eşleşiyor; değiştirilmiş paket reddediliyor
- [ ] (İsteğe bağlı) basit GUI + canlı ölçüm paneli
- **Çıkış:** iki ayrı makinede canlı demo; kurcalanmış paket testi geçiyor.

### Aşama 6 — Rapor ve sunum (18 – 31 Oca)
- [ ] Rapor (şartname şablonuna göre), "problem → iddia → kanıt → ürün" akışı
- [ ] Poster, 5 dakikalık sunum, demo senaryosu
- [ ] 30 olası jüri sorusu ve cevapları; iki öğrenci karşılıklı prova
- **Çıkış:** danışman onayı.

**Tampon:** 1 – 7 Şubat 2027.

## Riskler

| Risk | Etki | Önlem |
|---|---|---|
| Başvuru tarihi plandan erken | Yüksek | Aşama 0'da doğrula; gerekirse Aşama 5 GUI'si düşer |
| ML-KEM test vektörleri geçmiyor | Yüksek | Referans olarak bağımsız bir uygulamayla ara değer karşılaştırması |
| Hızlanma çıkmaz | Orta | Hipotez yine test edilmiş olur; "ne zaman hızlı, ne zaman değil" bulgusu raporlanır |
| Jüri "kodu siz mi yazdınız" sorusu | Yüksek | Kod okuma notları, karşılıklı anlatım, [06](06-acik-sorular.md)'daki beyan kararı |
| Pi'de ölçüm gürültüsü | Düşük | Sabit CPU frekansı notu, çok tekrar, medyan; laptopta tekrar |
