# Warren Buffett Analiz Metodolojisi

İki faz vardır. **Faz 1 tamamlanmadan Faz 2'ye geçme.**

## Faz 1 — Veri Toplama

1. `search_symbol(query=<şirket adı veya ticker>, market="bist")` → ticker'ı doğrula.
2. `get_profile(symbol=<ticker>, market="bist")` → sektör, iş modeli, temel finansallar.
   (Yeterlilik dairesi ve moat değerlendirmesi buradan beslenir.)
3. `get_financial_ratios(symbol=<ticker>, market="bist", ratio_set="buffett")` → **tüm sayısal
   değerleme tek atomik çağrıda gelir.**
4. Yalnızca DCF varsayımlarını tarihlemek/açıklamak gerekiyorsa: `get_bond_yields(country="TR")`
   ve `get_macro_data(data_type="inflation", inflation_type="tufe")`.

Ticker bulunamazsa veya oran seti boş dönerse: **durumu söyle ve dur.** Analiz uydurma.

### `ratio_set="buffett"` veri sözleşmesi

Yanıt düz anahtarlarla gelir:

| Alan | Anlamı | Not |
|---|---|---|
| `owner_earnings` | Owner Earnings, **milyon TL** | Net Kâr + Amortisman − CapEx − ΔİşletmeSermayesi. **Negatif olabilir.** |
| `oe_yield` | Yıllık OE / Piyasa Değeri | Ondalık (0.235 = %23,5). Buffett hedefi: **>0.10** |
| `dcf_intrinsic_value` | İçsel değer, **TL/hisse** | Fisher etkili reel iskonto ile hesaplanmış |
| `safety_margin` | (İçsel Değer − Fiyat) / İçsel Değer | Ondalık. **Negatif = hisse içsel değerin üzerinde.** Hedef: **>0.50** |
| `buffett_score` | Sunucunun sayısal verdiği etiket | `STRONG_BUY` · `BUY` · `HOLD` · `AVOID` |
| `insights` | Türkçe bulgu listesi | ✅ olumlu / ⚠️ uyarı / ❌ deal breaker |

**Negatif Owner Earnings durumunda** sunucu diğer alanları döndürmez, doğrudan `AVOID` verir.
Bu bir hata değildir — şirket nakit üretmiyor demektir. Sayıyı **olduğu gibi raporla, gizleme**.
(Bir şirket kâr açıklayıp yine de negatif OE üretebilir: yüksek CapEx veya işletme sermayesi
şişmesi kârı nakde çevirmiyordur. Bu, Buffett çerçevesinde tam olarak aranan sinyaldir.)

### Sayı üretme yasağı

Owner Earnings, OE Yield, içsel değer ve güvenlik marjını **sen hesaplamazsın** — MCP hesaplar,
sen yorumlarsın. Bu dört sayıyı yeniden türetmeye, düzeltmeye veya "tahmin etmeye" çalışma.

## Fisher Etkisi DCF — neden reel oran

Yüksek enflasyonda nominal iskonto oranıyla nominal nakit akışını karıştırmak değerlemeyi bozar.
Reel oran kullanılır:

    r_reel = (1 + r_nominal) / (1 + π) − 1 + risk primi

`r_nominal` → `get_bond_yields` (10Y TR tahvili), `π` → `get_macro_data` (TÜFE).
MCP bu hesabı zaten yapıyor; sen yalnızca **hangi varsayımlarla ve hangi tarihte** yapıldığını
raporda belirt. Girdiler çekilemezse "varsayım" olduğunu ve tarihini açıkça yaz.

---

## Karar Çerçevesi (BAĞLAYICI — tek otorite burasıdır)

Karar iki katmandan oluşur:

- **Sayısal katman (MCP):** `buffett_score`. Sen bunu değiştiremezsin, yeniden hesaplayamazsın.
- **Niteliksel katman (sen):** Yeterlilik Dairesi (CoC) ve Ekonomik Hendek (Moat) skorları.
  Bunlar kararı **yalnızca aşağı çekebilir, asla yukarı çıkaramaz.**

### Niteliksel skorlar (0.0 – 1.0)

**Yeterlilik Dairesi (CoC)** — "Bu işi gerçekten anlıyor muyum?"

| Alt kriter | 1.0 | 0.5 | 0.0 |
|---|---|---|---|
| İş modeli netliği | Tek cümlede anlatılır | 2–3 adım | Karmaşık |
| Ürün anlaşılabilirliği | Günlük hayattan | Sektörel | Teknik/opak |
| Gelir kaynakları | 1–2 kaynak | 3–5 | Dağınık |
| Sektör tahmin edilebilirliği | 10+ yıl öngörülebilir | ~5 yıl | Volatil |

`CoC = ortalama`. **Eşik: ≥0.70.** Altındaysa → "Too hard pile" (PAS).

**Ekonomik Hendek (Moat)** — `get_profile`'daki sektöre göre değerlendir.

| Alt kriter | 1.0 | 0.75 | 0.50 | 0.0 |
|---|---|---|---|---|
| Hendek tipi | Kaçınılmaz (çoklu, dominant) | Güçlü (tek dominant) | Orta (zayıf) | Yok |
| Sürdürülebilirlik | 20+ yıl | 10–20 yıl | 5–10 yıl | <5 yıl |
| Tehdit direnci | Çok yüksek | Düşük tehdit | Orta tehdit | Yüksek tehdit |

`Moat = (Tip × 0.40) + (Sürdürülebilirlik × 0.30) + (Tehdit direnci × 0.30)`. **Eşik: ≥0.60.**

### Deal Breaker'lar (analizi kes, doğrudan PAS)

1. `owner_earnings` ≤ 0 → "Şirket nakit üretmiyor, tüketiyor"
2. CoC < 0.70 → "Yeterlilik dairesi dışında"
3. Moat < 0.60 → "Sürdürülebilir rekabet avantajı yok"

### Nihai Karar Tablosu

| `buffett_score` | CoC ≥0.70 **ve** Moat ≥0.75 | CoC ≥0.70 **ve** Moat 0.60–0.75 | Deal breaker var |
|---|---|---|---|
| `STRONG_BUY` | ✅ **GÜÇLÜ AL** | ✅ **AL** | ❌ **PAS** |
| `BUY` | ✅ **AL** | 📊 **İZLE** | ❌ **PAS** |
| `HOLD` | 📊 **İZLE** | ⚠️ **TEMKİNLİ** | ❌ **PAS** |
| `AVOID` | ❌ **PAS** | ❌ **PAS** | ❌ **PAS** |

Başka eşik veya kademe kullanma. Sunucu etiketi ile kendi izlenimin çelişiyorsa **daha temkinli
olanı seç** ve nedenini yaz.

---

## Faz 2 — Rapor İskeleti (Türkçe markdown, 7 bölüm)

1. **🏢 Şirket Genel Bakış** — sektör, iş modeli, yeterlilik dairesi değerlendirmesi + CoC skoru
2. **💰 Owner Earnings** — `owner_earnings` (M TL). Negatifse bunu başlıkta söyle ve ne anlama
   geldiğini açıkla (kâr ≠ nakit).
3. **📊 OE Yield** — `oe_yield`, %10 hedefine göre yorum
4. **🎯 DCF Değerleme** — `dcf_intrinsic_value` (TL/hisse), kullanılan varsayımlar ve tarihleri
5. **🛡️ Güvenlik Marjı** — `safety_margin`, %50 hedefi. Negatifse "hisse içsel değerin üzerinde".
6. **🏰 Ekonomik Hendek** — sektöre özgü hendek tipi, sürdürülebilirlik, tehdit direnci + Moat skoru
7. **⚖️ Nihai Değerlendirme** — karar tablosundan çıkan sonuç + gerekçe + MCP `insights` bulguları

Rapor şununla biter:

`⚠️ Bu bilgiler yalnızca bilgilendirme amaçlıdır, yatırım tavsiyesi değildir.`

## Buffett'ın İki Kuralı

1. Asla para kaybetme.
2. Birinci kuralı asla unutma.

Şüphedeyken PAS de. Kaçırılan fırsatın maliyeti, kalıcı sermaye kaybının maliyetinden düşüktür.
