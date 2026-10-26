# 05 — Hata Kontrolü ve Kalite Kapıları

*Son güncelleme: 2026-10-26.*

## Doğruluk kaynakları (neye karşı test ediyoruz)
1. **Dış standart:** NIST ACVP ML-KEM test vektörleri. Bizim uygulamamızın doğru olduğunun tek bağımsız kanıtı.
2. **Altın standart:** okul yöntemi (schoolbook) negasiklik çarpım. Yavaş ama apaçık doğru; her yeni çarpım
   yöntemi buna karşı test edilir.
3. **Teori:** [04](04-teori.md)'teki sınırlar kodda `src/pqc/teori.py` olarak durur ve testlerle sayısal olarak
   kontrol edilir (ör. ℓ_min(η=3) = 22).

## Kod kuralları
- Her fonksiyonun yanında FIPS 203 algoritma numarası veya 04'teki lemma/teorem numarası yorum olarak yazılır.
- Yeni kod testi olmadan main'e girmez.
- CI (GitHub Actions) her push'ta `ruff check` + `pytest` çalıştırır. Kırmızı CI ile birleştirme yapılmaz.
- `experiments/00-on-olcum/` arşivdir; değiştirilmez, ruff'tan muaftır.

## Deney kuralları
- Sabit seed; seed `sonuc.md`'ye yazılır.
- Ham veri CSV olarak saklanır, elle düzenlenmez. Grafikler betikle üretilir.
- "Beklenen" değer deneyden **önce** [03](03-hipotez-ve-deneyler.md)'e yazılır.
- Her `sonuc.md`'de **"Bilinen kusurlar"** bölümü zorunludur.

## İddia etiketleri
Dokümanlarda sayı ve kaynaklar şu etiketlerden birini taşır:
- **[ölçüldü]** — repo içindeki bir betik üretti (betiğin yolu yazılır)
- **[hesaplandı]** — elle veya betikle türetildi, kontrol edildi
- **[doğrulanmadı]** — henüz kontrol edilmedi (YZ çıktısı dahil); raporda kullanılamaz

## Git akışı
- `main` her zaman çalışır durumda.
- Her aşama `asama-N` dalında yürür; aşama kapanınca kullanıcı onayıyla main'e birleştirilir.
- Commit mesajı Türkçe, kısa, ne ve neden.

## Aşama kapanış kontrol listesi
Bir aşama ancak bunların hepsi işaretliyse kapanır:
- [ ] Çıkış kriteri ([01](01-calisma-plani.md)) sağlandı
- [ ] CI yeşil
- [ ] `docs/kayit/YYYY-MM-DD-asama-N.md` yazıldı: ne yapıldı, ne bulundu, ne ters gitti, sonraki adım
- [ ] Öğrenciler kod okuma notunu kayda ekledi: hangi dosyayı okudu, ne anladı, hangi soru kaldı
- [ ] "Bana anlat" oturumu yapıldı (A ↔ B)
- [ ] README durum tablosu güncellendi
- [ ] [06](06-acik-sorular.md)'daki ilgili sorular kapandı veya ertelendi (gerekçesiyle)
