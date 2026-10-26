# 00 — Proje Özeti

*Son güncelleme: 2026-10-26 (Aşama 0). İlk taslak metnin yerini alır; abartılı iddialar çıkarıldı.*

## Tek cümle
ML-KEM'deki polinom çarpımını merkezlenmiş Kronecker ikamesiyle yapmak için gereken paketleme genişliğini
ispatlıyor, bu sınırı deneyle doğruluyor, sınırın altına inmenin güvenlik açığı doğurduğunu gösteriyor
ve yöntemi çalışan bir kuantum korumalı dosya aktarım prototipinde kullanıyoruz.

## Hikaye (rapor ve sunumun omurgası)

Danışman uyarısı: rapor anlatılmaz, **pazarlanır**. Her bölüm şu zinciri izler:
**problem → neden önemli → iddiamız → kanıtımız → çalışan ürün.**

1. **Problem.** RSA ve eliptik eğri tabanlı anahtar değişimi, Shor algoritması ile kuantum bilgisayarda polinom
   zamanda kırılabilir. Bugün kaydedilen trafik yarın çözülebilir ("harvest now, decrypt later").
2. **Çözümün standardı.** NIST, 13 Ağustos 2024'te FIPS 203 (ML-KEM) standardını yayımladı. Güvenliği
   Modül Üzerinde Hatalarla Öğrenme (Module-LWE) problemine dayanır; bilinen klasik ve kuantum saldırılarla
   pratikte kırılamaz kabul edilir.
3. **Bizim baktığımız yer.** ML-KEM'in her adımında `R_q = Z_3329[X]/(X^256+1)` halkasında bir polinom çarpımı
   vardır ve çarpanlardan biri her zaman küçük katsayılıdır (gizli s, r, e ∈ [−η, η], η ∈ {2, 3}).
   Standart bu çarpımı NTT ile yapar. Kronecker ikamesi ise polinomları büyük tamsayıya çevirip tek çarpım yapar.
4. **İddiamız.** Katsayıları merkezlenmiş tutmak paketleme genişliğini 32 → 22 bite indirir. Ama:
   - bu genişliğin **neden tam 22** olması gerektiği ispatlanmalı (teori),
   - teorinin öngördüğü eşik deneyle tutmalı (deney),
   - hızlanma, nerede ve hangi koşulda olduğu açıkça ölçülmeli (performans),
   - "ortalamada yeter" diye daha dar seçmek **güvensizdir**, bunu gösteriyoruz (güvenlik).
5. **Ürün.** PQC-Drop: iki bilgisayar arasında ML-KEM ile anahtar kurup dosyayı AES-256-GCM ile aktaran
   çalışan prototip. Teorinin gerçek bir sistemde iş gördüğünün kanıtı.

## Neden hibrit (KEM + AES)?
ML-KEM yalnızca 32 baytlık bir paylaşılan sır üretir. Dosyanın kendisi simetrik şifreyle (AES-256-GCM)
şifrelenir; Grover algoritması AES-256'nın etkin güvenliğini ~128 bite indirir, bu hâlâ yeterlidir.
Endüstride TLS 1.3 hibrit anahtar değişimi de aynı mantıkla çalışır.

## Ne söylüyoruz / ne söylemiyoruz

| Söylüyoruz | Söylemiyoruz |
|---|---|
| NIST standardını temel aldık | Yeni bir şifreleme algoritması bulduk |
| Literatürdeki işaretli Kronecker yöntemini ML-KEM için analiz ettik | Merkezlenmiş Kronecker'i ilk biz önerdik |
| Sınırı ispatladık ve deneyle doğruladık | Her koşulda daha hızlı |
| Python'da ölçtük; C'de sonuç farklı olabilir | Endüstriyel kullanıma hazır |
| Uygulamamız sabit zamanlı değildir (yan kanal) | Saldırılara karşı tam güvenli |

## Önceki taslaktan düzeltilen iddialar
- "ML-KEM süresinin %80'i polinom çarpımı" → **yanlış**; optimize uygulamalarda Keccak/SHAKE baskın. Çıkarıldı.
- "Literatürde Kronecker genellikle işaretsiz" → **yanlış**; işaretli varyantlar mevcut ([02](02-literatur.md)).
- "Halka üzerinde hatalarla öğrenme (Module-LWE)" → Module-LWE = *modül* üzerinde.
- "Taşma → decryption failure" → ayrı kavramlar. Taşma = yanlış çarpım (uygulama hatası);
  ML-KEM'in kendi çözme hatası olasılığı ~2⁻¹³⁹ mertebesindedir.
- Karşılaştırma yalnızca "işaretsiz vs işaretli Kronecker" değil; **NTT** (standardın yöntemi) asıl rakip.
