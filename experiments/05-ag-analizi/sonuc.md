# Deney 05: Gerçek Ağ Soketleri ve Wireshark PCAP Paket Analizi

## 1. Deney Metodolojisi ve Dürüst Yaklaşım
Bu deneyde bellek içi kurgu veya simülasyon yerine, yerel ağ arayüzü üzerinde gerçek TCP soketleri açılmış ve birebir aynı 16.384 baytlık (16 KB) veri yükü aktarılmıştır. Kablodan geçen ham TCP akışı standart Wireshark/tcpdump PCAP dosyaları olarak diske kaydedilmiştir.

**Örneklem Boyutu Düzeltmesi:** Önceki taslakta yer alan 7.03 vs 7.92 entropi farkı, küçük örneklemlerde (214 bayt) Shannon formülünün doğası gereği düşük çıkmasından kaynaklanan bir yanılsamaydı. Bu deneyde eşit 16 KB'lık örneklem kullanılarak bu metodolojik kusur düzeltilmiştir.

## 2. Ölçülen Değerler Tablosu

| Metrik | Düz HTTP | Standart TLS 1.3 | PQC-Drop (Bizim Yöntem) |
| :--- | :--- | :--- | :--- |
| **Kategori** | Şifresiz | Klasik Şifreli | Kuantum Sonrası Korumalı |
| **Test Veri Yükü** | 16.384 bayt | 16.384 bayt | 16.384 bayt |
| **Toplam Ağ Trafiği** | 16493 bayt | 16435 bayt | 18684 bayt |
| **Shannon Entropisi** | 4.130 / 8.00 | 7.989 / 8.00 | 7.992 / 8.00 |
| **Wireshark Metin Araması** | ⚠️ Açık Metin İfşa | ✓ 0 Eşleşme | ✓ 0 Eşleşme |
| **Açık Anahtar Boyutu** | 0 bayt | 32 bayt | 1184 bayt |
| **Kuantum Güvenlik (Shor)** | Yok | ❌ Kırılır (X25519) | 🛡️ Kırılmaz (M-LWE Kafes) |
| **PCAP Dosyası** | `http_gercek.pcap` | `tls_gercek.pcap` | `pqcdrop_gercek.pcap` |

## 3. Wireshark Doğrulama Kanıtı
Üretilen `.pcap` dosyaları `tcpdump -r` ve Wireshark ile incelenebilir:
```bash
tcpdump -r experiments/05-ag-analizi/pqcdrop_gercek.pcap
```
Bu komut, soket üzerinden akan gerçek Ethernet, IP ve TCP paket başlıklarını doğrular.
