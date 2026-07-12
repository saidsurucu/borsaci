# BorsaCI Skill

BorsaCI'nin Türk finans piyasaları uzmanlığını, skill + MCP destekleyen **herhangi bir** ajan
harness'ında çalışan saf-markdown bir skill olarak paketler. Kod içermez, bağımlılığı yoktur.

## Kurulum

### 1. Borsa MCP sunucusunu ekle

Skill'in **tek** veri kaynağıdır. Onsuz skill hiçbir şey yapmaz (fiyat uydurmaz, durur).

Claude Code:

```bash
claude mcp add --transport http borsa https://borsa.surucu.dev/mcp
```

claude.ai veya diğer harness'lar: Streamable HTTP MCP sunucusu olarak
`https://borsa.surucu.dev/mcp` adresini ekle.

> Eski `https://borsamcp.fastmcp.app/mcp` adresi **emekliye ayrıldı**, veri servis etmiyor.

### 2. Skill'i yükle

```bash
cp -r skill/borsaci ~/.claude/skills/
```

## Kullanım

Şu sorular skill'i tetikler:

- "ASELS son fiyatı nedir?"
- "ASELS THYAO GARAN son fiyatlarını karşılaştır"
- "GARAN'ı buffett gibi analiz et"
- "ASELS 1 aylık mum grafik"
- "En iyi performans gösteren 5 TEFAS fonu"
- "Bitcoin kaç TL?"

## Yapı

| Dosya | İçerik |
|---|---|
| `SKILL.md` | Tetikleme, preflight, yönlendirme, yürütme sözleşmesi, cevap formatı |
| `references/tools.md` | 28 Borsa MCP aracının kataloğu ve parametreleri |
| `references/planning.md` | Atomik görev, `depends_on`, paralellik kuralları |
| `references/buffett.md` | Buffett veri sözleşmesi ve tek otoriter karar tablosu |

Referans dosyaları yalnızca gerektiğinde okunur (progressive disclosure).

## Sürüm ve Uyumluluk

- Skill sürümü: **0.1.0**
- Borsa MCP: Unified API, **28 araç** (canlı şemaya karşı doğrulandı: 12.07.2026)

## Bu skill ile `src/borsaci/` ilişkisi

**Bağımsızdırlar ve senkron tutulmazlar.**

Python uygulaması (`uv run borsaci`) kendi ajan döngüsü ve kendi LLM sağlayıcısıyla
(PydanticAI + Gemini/OpenRouter) çalışır. Skill ise host'un modelini ve araç döngüsünü kullanır;
`src/` içinden hiçbir şey import etmez.

> Not: `src/borsaci/mcp_tools.py` hâlâ emekli `borsamcp.fastmcp.app` adresini varsayılan alıyor.
> Skill yeni adresi kullanır. Python tarafını düzeltmek ayrı bir iştir.

## Drift checklist (Borsa MCP değişirse)

1. Canlı araç listesini çek, `references/tools.md` ile karşılaştır, farkı düzelt.
   Çakışmada **canlı şema kazanır.**
2. `get_financial_ratios(ratio_set="buffett")` yanıt yapısı değiştiyse `references/buffett.md`
   içindeki veri sözleşmesi tablosunu güncelle.
3. Aşağıdaki kabul senaryolarını çalıştır.
4. `SKILL.md` içindeki sürüm numarasını artır.

## Kabul senaryoları

| # | Sorgu | Beklenen |
|---|---|---|
| 1 | MCP bağlı değilken "ASELS fiyatı" | Skill durur, kurulum talimatı verir, **fiyat uydurmaz** |
| 2 | "Merhaba" / "P/E oranı nedir?" | Araç çağrısı yok, Türkçe yanıt + disclaimer |
| 3 | "Bitcoin kaç TL?" | `get_crypto_market`, as-of tarihli yanıt |
| 4 | "ASELS THYAO GARAN son fiyatları" | Üç bağımsız çağrı eşzamanlı, tek tablo |
| 5 | "Türk bankalarının son çeyrek karlılığını karşılaştır" | Önce bileşen listesi → tablolar → karşılaştırma; ara çıktılar taşınmış |
| 6 | "GARAN'ı buffet gibi analiz et" | `buffett.md` okunur, Faz 1 tamamlanır, 7 bölümlü rapor |
| 7 | "ASELS'i buffett gibi analiz et" | **Negatif Owner Earnings gizlenmez** (−6.124M TL), karar PAS |
| 8 | Buffett raporundan sonra "yani alayım mı?" | Yeni araç çağrısı yok, bağlamdan yanıt + disclaimer |
| 9 | Boş konuşmada "alayım mı?" | Veri çekilir, uydurulmaz |
| 10 | "ASELS 1 aylık mum grafik" | OHLC tablosu + trend her koşulda; ortam destekliyorsa görsel |
| 11 | Var olmayan ticker ("ZZZZZ fiyatı") | 3 denemeden fazla döngü yok, net "bulunamadı" |
| 12 | "Python'da liste nasıl sıralanır?" | Skill tetiklenmez / kapsam dışı der |
