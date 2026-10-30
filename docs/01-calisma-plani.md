# 01 — Çalışma Planı

*Son güncelleme: 2026-10-27 (Aşama 2 kodu). **Başvuru son tarihi: 4 Ocak 2027, 17.30** (şartname, Halil doğruladı).
Hedef yükleme tarihi: **2 Ocak 2027** — son güne bırakılmaz.*

## Ekip ve rol dağılımı

| Kişi | Ana sorumluluk | Yan sorumluluk |
|---|---|---|
| Öğrenci A (Halil) | Yazılım, deney altyapısı, kod okuma/analiz | Performans deneyleri, prototip |
| Öğrenci B | Teori: ispatlar, olasılık modeli, literatür | Rapor dili, grafiklerin yorumu |
| Danışman öğretmen | Aşama kapanış onayı, rapor okuma | Şartname uyumu |

Kural: **iki öğrenci de her şeyi anlatabilmeli.** Her aşama sonunda karşılıklı "bana anlat" oturumu yapılır
(A teoriyi, B kodu anlatır).

Süre ilk plandan 4 hafta kısa olduğu için A (yazılım) ve B (teori) **paralel** ilerler.
Başvuru sonrası (Ocak–sergi) dönemi prototip cilası, poster ve sunum içindir.

## Aşamalar

Her aşamanın bir **çıkış kriteri** var. Kriter sağlanmadan sonraki aşamaya geçilmez
(bkz. [05 — Hata kontrolü](05-hata-kontrol.md)).

| Aşama | Tarih | Kim | Konu |
|---|---|---|---|
| 0 | 26 Eki – 2 Kas | A+B | Kurulum, danışman toplantısı |
| 1 | 3 – 15 Kas | **B** (A destek) | Literatür + teori |
| 2 | 3 – 22 Kas | **A** (B destek) | Referans ML-KEM + NIST test vektörleri |
| 3 | 23 Kas – 4 Ara | A | Kronecker motorları |
| 4 | 5 – 18 Ara | A+B | Deneyler (H2–H4) |
| 5a | 12 – 20 Ara | A | PQC-Drop **asgari** prototip (CLI) |
| 6 | 16 – 31 Ara | B önde, A+B | Rapor |
| — | 1 – 2 Oca | A+B | Son okuma, **yükleme (2 Ocak)** |
| — | 3 – 4 Oca | — | Tampon (yalnızca acil düzeltme) |
| 5b | Ocak – sergi | A+B | GUI, canlı ölçüm paneli, poster, sunum, jüri provası |

### Aşama 0 — Kurulum (26 Eki – 2 Kas 2026)
- [x] Repo iskeleti, dokümanlar, CI
- [x] Ön ölçüm betiği arşivlendi ([experiments/00-on-olcum](../experiments/00-on-olcum/sonuc.md))
- [x] Şartname okundu; son tarih 4 Ocak 2027 17.30
- [ ] Danışmanla toplantı: plan + [06 — Açık sorular](06-acik-sorular.md)
- **Çıkış:** danışman planı gördü; S3 (YZ beyanı) için karar tarihi belli.

### Aşama 1 — Literatür ve teori (3 – 15 Kas) · Öğrenci B
- [ ] [02](02-literatur.md)'deki her kaynağı bul, oku, künyesini doğrula (✘ → ✔)
- [ ] FIPS 203'ün ilgili bölümlerini oku: parametreler, CBD, NTT, K-PKE
- [x] Çıkış gözlemi (23², elde) teoriye bağlandı ([04 §0](04-teori.md), `src/pqc/taban.py`)
- [x] Lemma 1, Teorem 1, Önerme 1 kesin ifade + ispat yazıldı (Claude)
- [ ] B ispatları elle kontrol etti, keskinlik örneğini elle hesapladı
- [ ] Olasılık modelini (normal yaklaşım) kur
- [ ] Kategori kararı (Matematik / Bilgisayar)
- **Çıkış:** iki öğrenci de ispatı tahtada anlatıyor; 02 tablosunda ✘ kalmadı; kategori yazıldı.

### Aşama 2 — Referans ML-KEM (3 – 22 Kas) · Öğrenci A
- [x] Saf Python ML-KEM-512/768/1024: SHAKE, CBD, NTT, K-PKE, KEM (FIPS 203 algoritma numaralarıyla)
- [x] NIST ACVP test vektörleri ile test (keyGen, encaps, decaps)
- [x] Okul yöntemi (schoolbook) negasiklik çarpım = altın standart
- [ ] Halil'in kod okuma notu ([rehber](kod-okuma/asama-2.md))
- **Çıkış:** tüm resmî test vektörleri geçiyor; CI yeşil.

### Aşama 3 — Kronecker motorları (23 Kas – 4 Ara)
- [x] Varyantlar (8): işaretsiz 32 bit (döngü/bayt) · işaretli 22 bit · bayt hizalı 24 bit (ofset hilesi) ·
      mod 2^(nℓ)+1 negasiklik · modül toplamını paketli alanda yapan ([kronecker.py](../src/pqc/kronecker.py))
- [x] Her varyant ML-KEM'e takılabilir (`KroneckerPKE`, ADR 0003)
- [x] Kenar durum testleri; ML-KEM test vektörleri 8 varyantla geçiyor
- [x] 10.000 rastgele örnek (E1.2): 8 varyant, 0 hata ([sonuç](../experiments/01-dogruluk/sonuc.md))
- [ ] Halil'in kod okuma notu ([rehber](kod-okuma/asama-3.md))
- **Çıkış:** H1 doğrulandı.

### Aşama 4 — Deneyler (5 – 18 Ara)
- [x] H2: teorik eşik vs ölçülen eşik; olasılık modeli vs ölçülen hata oranı (grafik) — **öncelik 1**
- [x] H4: dar ℓ ile gizli anahtara bağlı hata gösterimi — **öncelik 2**
- [x] H3: performans (tek çarpım + tam keygen/encaps/decaps), ≥1000 tekrar, medyan + çeyrekler arası aralık
- **Çıkış:** her deney klasöründe betik + ham CSV + grafik + sonuc.md; betik tek komutla yeniden üretiyor.

### Aşama 5a — Asgari prototip (12 – 20 Ara)
- [x] CLI: `pqcdrop alici` / `pqcdrop gonder dosya ip`
- [x] El sıkışma: ML-KEM (bizim Kronecker motorumuzla) → HKDF → AES-256-GCM parça parça akış
- [x] Bütünlük: alınan dosyanın SHA-256'sı eşleşiyor; değiştirilmiş paket reddediliyor
- [ ] İki makine arası fiziksel aktarım (Pardus 1 ↔ Pardus 2) + `tcpdump -w` ile gerçek ağ kaydı (pcap) ve ekran
      görüntüsü — **Halil yapıyor (30 Eki)**. `experiments/05-ag-analizi` şu an yalnızca betik içi simülasyondur.
- [ ] Hedef makinede `python3 -c "import cryptography"` ile "sıfır kurulum" iddiası doğrulanacak.
- **Çıkış:** iki makine arası aktarım çalışıyor; rapora pcap özeti + ekran görüntüsü + ölçüm girecek kadar.

### Aşama 6 — Rapor (16 – 31 Ara)
- [x] Taslak 0 (30 Eki): [taslakfable.md](taslakfable.md) — örnek raporların düzeniyle; `[…]` yerleri doldurulacak
- [ ] [analiz-fable.md](analiz-fable.md)'deki "karar sizin" maddeleri: kaynak doğrulama (02'deki ✘'ler), YZ beyanı (S3),
      kategori (S4), E5 gerçek kayıt, E3.5
- [ ] Taslak 1: 22 Ara · danışman okuması: 23–26 Ara · son hali: 31 Ara
- **Çıkış:** danışman onayı; 2 Ocak'ta yükleme.

### Aşama 5b — Sergi hazırlığı (başvuru sonrası)
- [ ] Basit GUI + canlı ölçüm paneli, poster, 5 dakikalık sunum, demo senaryosu
- [ ] 30 olası jüri sorusu ve cevapları; iki öğrenci karşılıklı prova

## Kesilecekler listesi (takvim kayarsa, bu sırayla)
1. Aşama 5a'nın iki makine testi → tek makinede iki terminal
2. H3'te ikinci makine (laptop) ölçümü
3. Modül toplamını paketli yapan Kronecker varyantı
4. ML-KEM-1024 (512 ve 768 yeterli)

**Kesilmez:** H1 (test vektörleri), H2 (teori = deney), rapor.

## Riskler

| Risk | Etki | Önlem |
|---|---|---|
| Takvim sıkışık (10 hafta) | Yüksek | Paralel iş bölümü; kesilecekler listesi; 2 Ocak hedefi |
| Aralık sonu okul sınavları / tatil | Orta | Rapor taslağı 22 Ara'da hazır olmalı |
| ML-KEM test vektörleri geçmiyor | Yüksek | Bağımsız bir uygulamayla ara değer karşılaştırması |
| Hızlanma çıkmaz | Orta | Hipotez yine test edilmiş olur; "ne zaman hızlı, ne zaman değil" bulgusu raporlanır |
| Jüri "kodu siz mi yazdınız" sorusu | Yüksek | Kod okuma notları, karşılıklı anlatım, [06](06-acik-sorular.md)'daki beyan kararı |
| Pi'de ölçüm gürültüsü | Düşük | Çok tekrar, medyan, `gc` kapalı |
