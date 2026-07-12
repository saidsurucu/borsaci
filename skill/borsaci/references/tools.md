# Borsa MCP Araç Kataloğu

28 araç. Bu katalog bir haritadır — **canlı MCP şeması otoriterdir**. Bir araç burada
yazandan farklı parametre bekliyorsa şemaya uy ve bu dosyayı güncelle (bkz. README → Drift checklist).

Ortak parametreler:
- `symbol` — tek sembol (bazı araçlar virgüllü çoklu sembolü destekler, "Batch up to 10" yazanlar).
- `market` — `bist` | `us` | `crypto_tr` | `crypto_global` | `fund` | `fx`. Çoğu araçta **zorunlu**.
- `*` işareti zorunlu parametreyi gösterir.

---

## BIST — Hisse ve Endeks

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `search_symbol` | İsim/sembolden arama. **Ticker bilinmiyorsa ilk adım budur.** | `query*`, `market*`, `limit` |
| `get_profile` | Şirket profili: sektör, temel finansallar, ana metrikler, katılım uygunluğu | `symbol*`, `market*`, `include_islamic` |
| `get_quick_info` | Ana metrikler: P/E, P/B, ROE, 52 hafta aralığı. 10 sembole kadar toplu. | `symbol*`, `market*` |
| `get_historical_data` | **OHLCV** fiyat geçmişi. Grafik/mum grafik için tek doğru araç. | `symbol*`, `market*`, `period` (`1d\|5d\|1mo\|3mo\|6mo\|1y\|2y\|5y\|ytd\|max`), `start_date`, `end_date`, `adjust` |
| `get_technical_analysis` | RSI, MACD, Bollinger, hareketli ortalamalar, trend sinyalleri | `symbol*`, `market*`, `timeframe` (`1m\|5m\|15m\|30m\|1h\|4h\|1d\|1W`) |
| `get_pivot_points` | Klasik pivot: PP, S1–S3, R1–R3 ve en yakın seviyeye uzaklık | `symbol*`, `market*` |
| `get_analyst_data` | Analist tavsiyeleri, hedef fiyat, al/sat/tut dağılımı | `symbol*`, `market*` |
| `get_dividends` | Temettü verimi, geçmişi, dağıtım oranı, bölünmeler | `symbol*`, `market*` |
| `get_earnings` | Bilanço tarihleri, EPS geçmişi, sürprizler, büyüme tahminleri | `symbol*`, `market*` |
| `get_financial_statements` | Bilanço / gelir tablosu / nakit akışı | `symbol*`, `market*`, `statement_type` (`balance\|income\|cashflow\|all`), `period` (`annual\|quarterly`), `last_n` |
| `get_financial_ratios` | Oran setleri **ve Buffett analizi** | `symbol*`, `market*`, `ratio_set` (`valuation\|buffett\|core_health\|advanced\|comprehensive`) |
| `get_corporate_actions` | Bedelli/bedelsiz sermaye artırımı, halka arz, temettü işlemleri | `symbol*`, `year` |
| `get_news` | KAP haber listesi; `news_id` verilirse tam içerik | `symbol`, `news_id`, `limit`, `page` |
| `get_sector_comparison` | Sektör emsalleri, ortalama P/E ve P/B, göreli konum | `symbol*`, `market*` |
| `get_index_data` | Endeks değeri, değişim, istenirse bileşen hisseler | `code*` (BIST: `XU100`, `XU030`), `market*`, `include_components` |
| `screen_securities` | Temel tarama, 24 preset veya özel filtre | `market*`, `preset` (`value_stocks\|growth_stocks\|dividend_stocks\|large_cap\|mid_cap\|small_cap`), `custom_filters`, `security_type`, `limit` |
| `scan_stocks` | Teknik tarama (RSI, MACD, Supertrend, T3) | `index*` (`XU030\|XU100\|XBANK\|XUSIN\|XUMAL\|XUHIZ\|XUTEK\|XHOLD\|XGIDA\|XELKT\|XILTM\|XK10`), `preset`, `condition`, `timeframe` |

## TEFAS — Yatırım Fonları

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_fund_data` | Fon bilgisi, getiriler (günlük→5y), portföy dağılımı, fon karşılaştırma | `symbol*`, `include_performance`, `include_portfolio`, `compare_mode`, `start_date`, `end_date` |
| `screen_funds` | Fon tarama: tür, kategori, getiri filtresi, sıralama | `fund_type` (`YAT\|EMK`), `category`, `min_return_1m`, `min_return_1y`, `sort_by`, `limit` |
| `get_regulations` | SPK fon mevzuatı dokümantasyonu | `regulation_type` |

## Kripto

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_crypto_market` | Ticker, orderbook, işlemler veya OHLC | `symbol*`, `exchange*` (`btcturk` = TRY pariteleri, `coinbase` = USD pariteleri), `data_type` (`ticker\|orderbook\|trades\|exchange_info\|ohlc`) |

## Döviz, Kıymetli Maden, Emtia

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_fx_data` | 65 döviz, kıymetli maden ve emtia. Güncel veya geçmiş OHLC. | `symbol`, `category`, `data_type` (`current\|historical`), `start_date`, `end_date` |

## Makro

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_macro_data` | TÜFE/ÜFE enflasyon verisi; iki tarih arası kümülatif enflasyon hesabı | `data_type*` (`inflation\|calculate`), `inflation_type` (`tufe\|ufe`), `start_date`/`end_date` veya `start_year`/`end_year`, `basket_value`, `limit` |
| `get_bond_yields` | Devlet tahvili getirileri (2Y, 5Y, 10Y) ve **DCF için risksiz faiz** | `country` (`TR\|US`) |
| `get_economic_calendar` | 7 ülke ekonomik takvimi, önem filtresiyle | `country` (`TR\|US\|EU\|DE\|GB\|JP\|CN`), `importance`, `period` |
| `get_evds_data` | TCMB EVDS: 145 kategori, on binlerce makro seri (faiz, kur, ödemeler dengesi, enflasyon, beklenti anketleri) | `action*` (`categories\|datagroups\|series_list\|search\|series_info\|das`), `series_code(s)`, `frequency`, `formula`, `period`, `start_date`/`end_date`, `lang` |

## Yardımcı

| Araç | Ne yapar | Parametreler |
|---|---|---|
| `get_screener_help` | Tarama dokümantasyonu: 24 preset, filtre alanları, operatörler | `market*` |
| `get_scanner_help` | Teknik tarama dokümantasyonu: indikatörler, operatörler, 22 preset | — |

---

## Seçim Kuralları

1. **Ticker bilinmiyorsa** → `search_symbol`. "Aselsan" → ASELS, "Türk Hava Yolları" → THYAO.
   Türkçe karakterleri (ç, ğ, ı, ö, ş, ü) olduğu gibi ara.
2. **"Fiyat" sorusu** tek bir sayı istiyorsa → `get_quick_info`.
   **Grafik / mum grafik / OHLC** isteniyorsa → `get_historical_data` (kapanış serisi yetmez;
   Open-High-Low-Close gerekir). Kripto için → `get_crypto_market(data_type="ohlc")`.
3. **Tarama** isteğinde preset veya filtre adından emin değilsen → önce `get_screener_help`
   (temel) ya da `get_scanner_help` (teknik). Preset uydurma.
4. **Makro veri**: enflasyon → `get_macro_data`; tahvil faizi / risksiz oran → `get_bond_yields`;
   bunların dışındaki her makro seri (kur, faiz koridoru, ödemeler dengesi, beklenti anketi) → `get_evds_data`.
5. **Araç hata verirse** aynı argümanla tekrar deneme. Sembol hatası olabilir → `search_symbol`
   ile doğrula, sonra alternatif araca geç.
6. Araç yanıtındaki sayıları **ham** kullan; yeniden hesaplama, yuvarlama, "düzeltme" yapma.
