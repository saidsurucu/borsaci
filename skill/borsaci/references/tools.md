# Borsa MCP Araç Kataloğu

23 araç. Bu katalog bir haritadır — **canlı MCP şeması otoriterdir**. Bir araç burada
yazandan farklı parametre bekliyorsa şemaya uy ve bu dosyayı güncelle (bkz. README → Drift checklist).

Ortak parametreler:
- `symbol` — tek sembol veya liste (çoğu araç **10 sembole kadar toplu** çağrıyı destekler).
- `market` — araca göre `bist` | `us` | `fx` | `crypto` | `fund`. Çoğu araçta **zorunlu**.
- `*` işareti zorunlu parametreyi gösterir.

---

## Fiyat ve Piyasa

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `search_symbol` | İsim/sembolden arama. **Ticker bilinmiyorsa ilk adım budur.** | `query*`, `market*` (`bist\|us\|crypto\|fx\|fund`), `limit` |
| `get_quote` | **"Şu an ne ediyor":** hisse (P/E, P/B, 52h aralığı ile), döviz, kıymetli maden, kripto. 10 sembole kadar toplu. | `symbol*`, `market*` (`bist\|us\|fx\|crypto`), `exchange` |
| `get_historical_data` | **OHLCV** fiyat geçmişi. Grafik/mum grafik için tek doğru araç. | `symbol*`, `market*` (`bist\|us\|fx\|crypto\|fund`), `period` (`1d\|5d\|1mo\|3mo\|6mo\|1y\|2y\|5y\|ytd\|max`), `start_date`, `end_date`, `exchange`, `adjust` |
| `compare_assets` | **Farklı piyasaları tek tabloda karşılaştır:** BIST/ABD hissesi, altın, döviz, kripto, TEFAS fonu — TRY ve USD getirisi birlikte. | `assets*` (10'a kadar; ör. `["ASELS","gram-altin","USD"]`), `start_date*`, `end_date`, `base_currency` (`TRY\|USD`), `initial_amount` |
| `get_crypto_market` | Kripto ticker, orderbook, işlemler, OHLC | `symbol*` (BTCTRY, BTC-USD), `exchange*` (`btcturk` = TRY, `coinbase` = USD), `data_type` (`ticker\|orderbook\|trades\|exchange_info\|ohlc`) |
| `get_index_data` | Endeks değeri, değişim, istenirse bileşen hisseler | `code*` (BIST: `XU100`, `XU030`), `market*`, `include_components` |

**Sembol biçimleri** (`get_quote` / `compare_assets`): hisse → `GARAN`, `AAPL` · döviz ve maden →
`USD`, `EUR`, `gram-altin`, `gram-gumus`, `BRENT` · kripto → `BTCTRY`, `BTC-USD` · fon → `TI2`.

## Şirket ve Finansallar

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_profile` | Şirket profili: sektör, temel finansallar, ana metrikler, katılım uygunluğu | `symbol*`, `market*` (`bist\|us\|fund`), `include_islamic` |
| `get_financial_statements` | Bilanço / gelir tablosu / nakit akışı | `symbol*`, `market*`, `statement_type` (`balance\|income\|cashflow\|all`), `period` (`annual\|quarterly`), `last_n` |
| `get_financial_ratios` | Oran setleri **ve Buffett analizi** | `symbol*`, `market*`, `ratio_set` (`valuation\|buffett\|core_health\|advanced\|comprehensive`) |
| `get_earnings` | Bilanço tarihleri, EPS geçmişi, sürprizler, büyüme tahminleri | `symbol*`, `market*` |
| `get_analyst_data` | Analist tavsiyeleri, hedef fiyat, al/sat/tut dağılımı | `symbol*`, `market*` |
| `get_corporate_actions` | **Şirket ne dağıttı/ne ihraç etti:** temettü, bölünme, (BIST) bedelli/bedelsiz sermaye artırımı | `symbol*`, `market`, `year` |
| `get_sector_comparison` | Sektör emsalleri, ortalama P/E ve P/B, göreli konum | `symbol*`, `market*` |
| `get_news` | KAP haber listesi; `news_id` verilirse tam içerik | `symbol`, `news_id`, `limit`, `page` |

## Teknik Analiz ve Tarama

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_technical_analysis` | RSI, MACD, Bollinger, hareketli ortalamalar, trend sinyalleri. **`include_pivots=true` ile pivot seviyeleri** (PP, R1–R3, S1–S3; sadece bist/us). | `symbol*`, `market*` (`bist\|us\|crypto`), `timeframe` (`1m\|5m\|15m\|30m\|1h\|4h\|1d\|1W`), `include_pivots`, `exchange` |
| `screen_securities` | Temel tarama: 24 preset (`value_stocks`, `growth_stocks`, `dividend_stocks`, `undervalued`, `top_gainers`, sektör presetleri…) veya özel filtre | `market*`, `preset`, `custom_filters`, `security_type`, `limit`, **`help=true`** → presetleri/filtreleri döndürür |
| `scan_stocks` | Teknik tarama (RSI, MACD, Supertrend, T3) | `index` (`XU030\|XU100\|XBANK\|XUSIN\|XUMAL\|XUHIZ\|XUTEK\|XHOLD\|XGIDA\|XELKT\|XILTM\|XK100\|XK050\|XK030`), `preset`, `condition`, `timeframe`, **`help=true`** |

Preset veya filtre adından emin değilsen **önce `help=true` ile çağır** — preset uydurma.

## TEFAS Fonları

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_fund_data` | Fon bilgisi ve getiriler (günlük→5y), portföy, fon karşılaştırma. **`data_type="regulations"` → SPK fon mevzuatı** (sembol gerekmez). | `symbol`, `data_type` (`fund\|regulations`), `include_performance`, `include_portfolio`, `compare_mode`, `start_date`, `end_date` |
| `screen_funds` | Fon tarama: tür, kategori, getiri filtresi, sıralama | `fund_type` (`YAT\|EMK`), `category`, `min_return_1m`, `min_return_1y`, `sort_by`, `limit` |

> Not: 2026-04 TEFAS geçişinden sonra `include_portfolio` portföy dağılımını döndürmeyebilir
> (`portfolio=null` + uyarı). Bu bir hata değildir; kullanıcıya olduğu gibi aktar.

## Makro

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_macro_data` | Enflasyon ve satın alma gücü hesabı: TR (TÜFE/ÜFE), ABD (CPI-U), Euro Bölgesi (HICP) | `data_type*` (`inflation\|calculate`), `region` (`tr\|us\|eu`), `inflation_type` (`tufe\|ufe`, yalnız TR), tarih/yıl-ay aralığı, `basket_value`, `limit` |
| `get_bond_yields` | Devlet tahvili getirileri (2Y, 5Y, 10Y) ve **DCF için risksiz faiz** | `country` |
| `get_economic_calendar` | 7 ülke ekonomik takvimi, önem filtresiyle | `country` (`TR\|US\|EU\|DE\|GB\|JP\|CN`), `importance`, `period` |
| `get_evds_data` | TCMB EVDS: 145 kategori, on binlerce makro seri (faiz, kur, ödemeler dengesi, enflasyon, beklenti anketleri) | `action*` (`categories\|datagroups\|series_list\|search\|series_info\|dashboards…`), `series_code(s)`, `frequency`, `formula`, `period`, tarih aralığı, `lang` |

---

## Seçim Kuralları

1. **Ticker bilinmiyorsa** → `search_symbol`. "Aselsan" → ASELS, "Türk Hava Yolları" → THYAO.
   Türkçe karakterleri (ç, ğ, ı, ö, ş, ü) olduğu gibi ara.
2. **"Şu an kaç para?"** (hisse, dolar, altın, Bitcoin) → `get_quote`. Tek çağrıda 10 sembol
   sorabilirsin, farklı piyasalar için ayrı çağrı gerekir (`market` farklı).
3. **Grafik / mum grafik / OHLC** → `get_historical_data` (kapanış serisi yetmez;
   Open-High-Low-Close gerekir). Kripto için `market="crypto"` ya da
   `get_crypto_market(data_type="ohlc")`.
4. **"X mi Y mi daha çok kazandırdı?"** (farklı varlık sınıfları, dönem getirisi) → `compare_assets`.
   Hisse + altın + dolar + fonu tek tabloda, TRY ve USD cinsinden verir. Elle hesaplama yapma.
5. **Pivot / destek-direnç** → `get_technical_analysis(include_pivots=true)`. Ayrı bir pivot aracı yok.
6. **Temettü geçmişi** → `get_corporate_actions` (bölünme ve sermaye artırımını da o döndürür).
7. **Tarama** presetinden emin değilsen → `screen_securities(help=true)` veya `scan_stocks(help=true)`.
8. **Fon mevzuatı** → `get_fund_data(data_type="regulations")`.
9. **Makro veri**: enflasyon → `get_macro_data`; tahvil faizi / risksiz oran → `get_bond_yields`;
   bunların dışındaki her makro seri (kur, faiz koridoru, ödemeler dengesi, beklenti anketi) → `get_evds_data`.
10. **Araç hata verirse** aynı argümanla tekrar deneme. Sembol hatası olabilir → `search_symbol`
    ile doğrula, sonra alternatif araca geç.
11. Araç yanıtındaki sayıları **ham** kullan; yeniden hesaplama, yuvarlama, "düzeltme" yapma.
