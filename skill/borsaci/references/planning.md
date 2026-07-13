# Görev Planlama ve Paralellik

Karmaşık sorgularda (birden fazla varlık, karşılaştırma, çok adımlı analiz) veri toplamaya
başlamadan önce **açık bir görev listesi** çıkar. Tek adımlı sorularda plan yapma, doğrudan aracı çağır.

## Görev Formatı

Her görev: `id`, Türkçe açıklama, kullanılacak araç, `depends_on` (bağlı olduğu görev id'leri).

| id | Görev | Araç | depends_on |
|----|-------|------|-----------|
| 1 | ASELS teknik analizi | `get_technical_analysis` | — |
| 2 | ASELS analist hedef fiyatları | `get_analyst_data` | — |
| 3 | İkisini birlikte yorumla | (araç yok, analiz) | 1, 2 |

> Aynı veriyi birden çok sembol için istiyorsan **görev çoğaltma** — çoğu araç 10 sembole kadar
> toplu çağrıyı destekler: `get_quote(symbol=["ASELS","THYAO","GARAN"], market="bist")` tek görevdir.

## Kurallar

1. **Atomik ol.** Bir görev = bir araç çağrısı.
   ❌ "ASELS ve THYAO'yu analiz et"
   ✅ "ASELS profilini al" · "THYAO profilini al" · "Karşılaştır"

2. **Bağımsız görevleri paralel çağır.** Aynı anda en fazla **5** araç çağrısı.
   `depends_on: []` olan her görev diğerlerinden bağımsızdır.

3. **Bağımlı görevde çıktıyı açıkça taşı.** Bağlı olunan görevin sonucunu değeriyle kullan —
   "önceki adımda bulduğum ticker" diye ima etme, ticker'ı yaz.

4. **Görev başına en fazla 3 deneme.** Üçüncüde de veri gelmezse görevi başarısız işaretle,
   kısmi sonuçla devam et ve kullanıcıya neyin eksik kaldığını söyle.

5. **Aynı aracı aynı argümanlarla iki kez çağırma.** Başarısızsa ya argümanı değiştir
   (sembolü `search_symbol` ile doğrula) ya da alternatif araca geç.

6. **Kapsam dışıysa görev üretme.** Soru Türk finans piyasalarıyla ilgili değilse plan yapma,
   kapsam dışı olduğunu söyle.

## Önce toplu çağrıyı düşün

Aynı aracın aynı `market` değeriyle birden çok sembol istediği durumda **görev çoğaltma**:
`get_quote`, `get_profile`, `get_financial_ratios`, `get_technical_analysis`,
`get_corporate_actions`, `get_analyst_data`, `get_earnings`, `get_financial_statements`
10 sembole kadar toplu çağrıyı destekler.

- ✅ Tek görev: `get_quote(symbol=["ASELS","THYAO","GARAN"], market="bist")`
- ❌ Üç ayrı görev: "ASELS fiyatı", "THYAO fiyatı", "GARAN fiyatı"

Farklı varlık sınıflarının **dönem getirisini** karşılaştırıyorsan tek araç yeter:
`compare_assets(assets=["ASELS","gram-altin","USD"], start_date=…)`.

## Paralel-Güvenli Örnekler (`depends_on: []`)

Toplu çağrının çözmediği, gerçekten bağımsız görevler:

- Farklı **piyasalar** (ayrı `market` gerektirir): `get_quote(["ASELS"], "bist")` ·
  `get_quote(["gram-altin"], "fx")` · `get_quote(["BTCTRY"], "crypto")`
- Aynı şirketin **farklı veri türleri**: "ASELS finansalları", "ASELS teknik analiz", "ASELS KAP haberleri"
- Farklı makro seriler: "TÜFE enflasyon", "10Y tahvil faizi"

## Sıralı Olması Gerekenler

- Ticker bilinmiyor → `search_symbol` **sonra** veri çekimi
- Veri topla → **sonra** hesapla / karşılaştır / sırala
- Tarama presetinden emin değilsin → `screen_securities(help=true)` **sonra** taramayı çalıştır

## Örnek: Çok Adımlı Karşılaştırma

Soru: *"Türk bankalarının son çeyrek karlılığını karşılaştır"*

| id | Görev | Araç | depends_on |
|----|-------|------|-----------|
| 1 | Banka endeksi bileşenlerini al | `get_index_data(code="XBANK", include_components=true)` | — |
| 2 | Her banka için son çeyrek gelir tablosu | `get_financial_statements(statement_type="income", period="quarterly", last_n=1)` | 1 |
| 3 | Net kâr marjlarını karşılaştır ve sırala | (araç yok, analiz) | 2 |

Görev 2'de bankalar 5'erli gruplar hâlinde paralel çağrılır (eşzamanlılık sınırı).

## Grafik / OHLC İstekleri

- BIST → `get_historical_data(symbol, market="bist", period)` — OHLCV döner
- Kripto → `get_crypto_market(symbol, exchange, data_type="ohlc")` veya `get_historical_data(market="crypto")`
- Döviz/altın/emtia → `get_historical_data(symbol="gram-altin", market="fx")`

❌ Sadece kapanış fiyatı mum grafik için yeterli değildir.
