# PQC-Kronecker — Kuantum Sonrası Anahtar Kapsüllemede Merkezlenmiş Kronecker İkamesi

TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması projesi.

**Problem.** Bugün şifrelenip kaydedilen veriler, ileride yeterince büyük bir kuantum bilgisayarla çözülebilir
("şimdi topla, sonra çöz"). NIST bu yüzden 2024'te kuantum sonrası anahtar kapsülleme standardı
**FIPS 203 (ML-KEM)**'i yayımladı. ML-KEM'in temel işlemi, `Z_3329[X]/(X^256+1)` halkasında polinom çarpımıdır.

**Ne yapıyoruz.** Bu çarpımı, polinomları tek bir büyük tamsayıya paketleyip tek seferde çarpan
**Kronecker ikamesi** ile yapıyoruz. ML-KEM'de çarpanlardan biri hep küçük katsayılı (gizli vektör, |s| ≤ 3)
olduğundan katsayıları merkezlenmiş (işaretli) tutarak paketleme genişliğini 32 bitten 22 bite indirebiliyoruz.

**Neyi kanıtlamak istiyoruz.**
1. Gereken paketleme genişliğini veren sınırı **ispatlamak**, sınırın keskin olduğunu göstermek ve teorik
   tahmini **deneyle doğrulamak**.
2. Bu yöntemin NTT, okul yöntemi ve Karatsuba'ya göre ne zaman, neden hızlı/yavaş olduğunu ölçmek.
3. Sınırın altına inmenin yalnızca hata değil, **güvenlik açığı** olduğunu göstermek.
4. Hepsini çalışan bir güvenli dosya aktarım prototipinde (**PQC-Drop**) bir araya getirmek.

> Yeni bir şifreleme algoritması icat etmiyoruz. NIST standardını temel alıyor, standardın içindeki
> çarpım işlemini literatürdeki bir yöntemin merkezlenmiş varyantıyla inceliyoruz.

## Durum

**Başvuru son tarihi: 4 Ocak 2027, 17.30** · hedef yükleme: 2 Ocak 2027

| Aşama | Konu | Tarih | Durum |
|---|---|---|---|
| 0 | Repo, plan, dokümanlar, ön ölçüm | 26 Eki – 2 Kas 2026 | 🟡 iskelet + CI hazır, danışman toplantısı bekliyor |
| 1 | Literatür + teori (ispat) | 3 – 15 Kas | 🟡 çıkış gözlemi (23²) + Lemma 1 / Teorem 1 ispatları yazıldı (`asama-1`), B'nin kontrolü ve künye doğrulama bekliyor |
| 2 | Referans ML-KEM (NTT) + NIST test vektörleri | 3 – 22 Kas | 🟡 kod + 225/225 NIST testi geçti (`asama-2` dalı), kod okuma bekliyor |
| 3 | Kronecker motorları + ML-KEM entegrasyonu | 23 Kas – 4 Ara | 🟡 8 varyant, her biri 225/225 NIST testi (`asama-3` dalı), kod okuma bekliyor |
| 4 | Deneyler (H2–H4) | 5 – 18 Ara | 🟡 H2 tamamlandı (200.000 deneme + Model 2 doğrulaması), H4 ve H3 bekliyor |
| 5a | PQC-Drop asgari prototip (CLI) | 12 – 20 Ara | ⏳ |
| 6 | Rapor | 16 – 31 Ara | ⏳ |
| 5b | GUI, poster, sunum (başvuru sonrası) | Ocak – sergi | ⏳ |

Ayrıntı: [docs/01-calisma-plani.md](docs/01-calisma-plani.md)

## Dokümanlar

- [00 — Proje özeti](docs/00-proje-ozeti.md)
- [01 — Çalışma planı](docs/01-calisma-plani.md)
- [02 — Literatür](docs/02-literatur.md)
- [03 — Hipotezler ve deneyler](docs/03-hipotez-ve-deneyler.md)
- [04 — Teori](docs/04-teori.md)
- [05 — Hata kontrolü ve kalite kapıları](docs/05-hata-kontrol.md)
- [06 — Açık sorular](docs/06-acik-sorular.md)
- [Aşama kayıtları](docs/kayit/) · [Kararlar (ADR)](docs/kararlar/) · [Kod okuma rehberleri](docs/kod-okuma/)

## Çalıştırma

```bash
python3 -m venv .venv && . .venv/bin/activate   # fish: . .venv/bin/activate.fish
pip install -e '.[dev]'
pytest                 # testler
ruff check .           # kod stili
python araclar/mutasyon_kontrolu.py              # testlerin hata yakalama gücü (~5 dk)
python experiments/00-on-olcum/ks_bench.py      # ön ölçüm (birkaç dakika)
python experiments/01-dogruluk/calistir.py      # E1.2: 10.000 örnek doğruluk deneyi
```

## Klasörler

```
docs/          plan, teori, literatür, kayıtlar, kararlar
src/pqc/       ML-KEM (FIPS 203) ve çarpım yöntemleri
tests/         otomatik testler (NIST ACVP vektörleri dahil)
araclar/       yardımcı araçlar (mutasyon kontrolü)
experiments/   her deney: betik + ham veri + sonuc.md
```
