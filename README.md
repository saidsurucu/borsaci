# BorsaCI 📊

**Türk Finans Piyasaları için AI Agent**

> 🔬 **Araştırma Projesi** | 📚 **Eğitim Amaçlı** | ⚠️ **Yatırım Tavsiyesi Değildir**
>
> Bu proje **tamamen eğitim ve araştırma amaçlı** geliştirilmiştir. Gerçek finansal kararlar için kullanılmamalıdır.

BorsaCI, Borsa MCP sunucusunu kullanarak BIST hisseleri, TEFAS fonları, kripto paralar, döviz kurları ve makro ekonomik verilere erişim sağlayan akıllı bir finansal asistanıdır.

## 🌟 Özellikler

- **43 Finansal Araç**: Borsa MCP ile entegre tam kapsamlı piyasa erişimi
- **Multi-Agent Architecture**: Görev planlama, yürütme, doğrulama ve yanıt sentezleme
- **Paralel Görev Yürütme**: Dependency-aware parallelization ile 50-70% performans artışı
- **Terminal Chart Visualization**: plotext ile renkli candlestick (mum) grafikleri
- **Conversation History**: Follow-up soru desteği ve konuşma bağlamı yönetimi
- **Markdown Rendering**: Rich formatlanmış terminal çıktısı
- **Auto-Update System**: GitHub commit-based otomatik güncelleme
- **Türkçe Native**: Tamamen Türkçe komutlar ve çıktılar
- **Type-Safe**: PydanticAI ile güvenli ve IDE-friendly geliştirme
- **Güçlü LLM**: Google Gemini 2.5 Series (Pro + Flash)
- **Cost-Effective**: OpenRouter ile esnek ve ekonomik model kullanımı

## 📦 Kapsam

### BIST (Borsa İstanbul)
- 758 şirket veritabanı
- Finansal tablolar (bilanço, gelir, nakit akışı)
- Teknik göstergeler (RSI, MACD, Bollinger Bands)
- Analist tavsiyeleri
- Endeks bileşenleri

### TEFAS (Yatırım Fonları)
- 800+ fon
- Kategori bazlı arama
- Portföy analizi
- Performans verileri

### Kripto Paralar
- BtcTurk: 295+ TRY bazlı parite
- Coinbase: 500+ USD/EUR bazlı parite
- Orderbook ve teknik analiz

### Makro Ekonomi
- Döviz kurları (28+ parite)
- Emtia fiyatları (altın, petrol, gümüş)
- TCMB enflasyon verileri (TÜFE, ÜFE)
- Ekonomik takvim (30+ ülke)

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenRouter API anahtarı ([buradan alın](https://openrouter.ai/keys))

### Adım Adım

```bash
# 1. Repository'i klonlayın
git clone https://github.com/saidsurucu/borsaci.git
cd borsaci

# 2. Dependencies'i yükleyin
uv sync

# 3. Çalıştırın
uv run borsaci
# İlk çalıştırmada OpenRouter API key'iniz otomatik olarak sorulacak
```

**Not:** CLI ilk çalıştırmada `OPENROUTER_API_KEY` bulamazsa sizden isteyecek ve otomatik olarak `.env` dosyasına kaydedecektir. Manuel kurulum yapmanıza gerek yok!

### Environment Variables (.env)

```bash
# Zorunlu
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Opsiyonel (OpenRouter rankings için)
HTTP_REFERER=https://borsaci.app
X_TITLE=BorsaCI

# Borsa MCP Server URL
BORSA_MCP_URL=https://borsamcp.fastmcp.app/mcp

# Agent konfigürasyonu
MAX_STEPS=20                    # Global maksimum adım sayısı (sonsuz döngü koruması)
MAX_STEPS_PER_TASK=5           # Görev başına maksimum deneme sayısı

# Performans
PARALLEL_EXECUTION=true         # Paralel görev yürütme (önerilen: true)
                               # false: Sıralı yürütme (debug için)
```

**Not:**
- `OPENROUTER_API_KEY` ilk çalıştırmada otomatik sorulur ve `.env` dosyasına kaydedilir
- `PARALLEL_EXECUTION=true` ile 50-70% performans artışı elde edilir
- Timeout değerleri: Planning (300s), Action (300s), Answer (300s)

## 💡 Kullanım

### İlk Çalıştırma

BorsaCI ilk kez çalıştırıldığında API key'inizi soracaktır:

```bash
$ uv run borsaci

╔══════════════════════════════════════════════════════════╗
║                     BORSACI                             ║
╚══════════════════════════════════════════════════════════╝

⚠️  Uyarı: OPENROUTER_API_KEY bulunamadı!
ℹ️  OpenRouter API key'inizi alın: https://openrouter.ai/keys

OpenRouter API Key: ••••••••••••••••••••••••••

✅ API key .env dosyasına kaydedildi!

ℹ️  BorsaCI başlatılıyor...
✅ Borsa MCP bağlantısı kuruldu (43 araç)

>>
```

### Interactive Mode

```bash
uv run borsaci
```

### Örnek Sorgular

**Temel Sorgular:**
```
>> ASELS hissesinin son çeyrek gelir büyümesi nedir?

>> En iyi performans gösteren 5 A tipi fonu listele

>> Bitcoin TRY fiyatı ve son 24 saatteki değişim ne?

>> Teknoloji sektöründeki şirketleri karşılaştır

>> Son enflasyon rakamları ve EUR/TRY kuru nedir?
```

**Grafik Sorguları:**
```
>> ASELS 1 haftalık mum grafik

>> THYAO candlestick chart göster

>> GARAN son 5 günlük fiyat grafiği
```

**Follow-Up Sorular:**
```
>> ASELS hissesi hakkında bilgi ver
[Detaylı analiz...]

>> detaylandır
[Önceki analizi derinleştirir]

>> alayım mı?
[Bağlamı kullanarak yanıt verir - yatırım tavsiyesi değil, risk analizi]

>> daha fazla bilgi ver
[Ek detaylar sağlar]
```

**Paralel Sorgular** (hızlı yanıt):
```
>> ASELS THYAO GARAN EREGL SAHOL son fiyatları
[5 hisse paralel sorgulanır - 50-70% daha hızlı]

>> Altın dolar euro bitcoin fiyatları
[4 farklı varlık paralel çekilir]
```

### Komutlar

- `exit`, `quit`, `çık` - Programdan çık
- `help`, `yardım` - Yardım göster
- `tools`, `araçlar` - Mevcut araçları listele
- `clear` - Ekranı temizle

## 🏗️ Mimari

BorsaCI, **Dexter** tarzı multi-agent pattern kullanır ve modern özelliklerle güçlendirilmiştir:

### 🔄 Agent Akışı

```
User Query
    ↓
Planning Agent → TaskList (with dependencies)
    ↓
Build Execution Plan (topological sort)
    ↓
For each dependency level:
    ↓
    If multiple tasks → Execute in parallel ⚡
    If single task → Execute sequentially
    ↓
    Action Agent → MCP Tool Call(s)
    ↓
    Validation Agent → IsDone?
    ↓ (if not done, retry)
    ↓
Answer Agent + Chart Generation → Final Response
```

### 1. Planning Agent
**Model**: Google Gemini 2.5 Pro (güçlü reasoning)

Kullanıcı sorgusunu atomik görevlere ayırır ve görevler arası bağımlılıkları tanımlar.

**Örnek:**
```
Sorgu: "ASELS THYAO GARAN son fiyatları"

Görevler:
[
  {id: 1, description: "ASELS fiyatı", depends_on: []},     # Bağımsız
  {id: 2, description: "THYAO fiyatı", depends_on: []},     # Bağımsız
  {id: 3, description: "GARAN fiyatı", depends_on: []}      # Bağımsız
]

→ 3 task paralel yürütülür (50-70% performans artışı)
```

**Follow-Up Detection**: "detaylandır", "alayım mı?" gibi devam sorularını tespit eder ve conversation history kullanır.

### 2. Action Agent
**Model**: Google Gemini 2.5 Flash (hızlı tool calling)

Her görev için uygun Borsa MCP aracını seçer ve çalıştırır. PydanticAI MCP toolset entegrasyonu ile LLM otomatik araç seçimi yapar.

**Araç Seçimi:**
- Şirket araması → `search_bist_companies`
- Finansal tablo → `get_company_financials`
- Fon araması → `search_funds`
- Kripto fiyat → `get_btcturk_ticker`, `get_coinbase_ticker`

### 3. Validation Agent
**Model**: Google Gemini 2.5 Flash (hızlı validation)

Görevin tamamlanıp tamamlanmadığını kontrol eder.

**Kriterler:**
- Yeterli veri toplandı mı?
- Kurtarılamaz hata oluştu mu?
- Scope dışında mı?

### 4. Answer Agent + Chart Generation
**Model**: Google Gemini 2.5 Flash (kaliteli Türkçe yanıt)

Toplanan verileri sentezleyerek kapsamlı Türkçe yanıt oluşturur ve gerekiyorsa chart generate eder.

**Format:**
- Veri odaklı analiz
- Sayılarla desteklenmiş
- Kaynak belirtme
- Yatırım tavsiyesi uyarısı
- **Chart generation** (LLM dışında, hallucination önleme)

### ⚡ Paralel Görev Yürütme

BorsaCI, bağımlılık-farkında paralel görev yürütme sistemi kullanır:

**Nasıl Çalışır?**
1. **Planning Agent bağımlılıkları tanımlar**: Her `Task` bir `depends_on: list[int]` listesi içerir
2. **Topological sort**: Kahn algoritması ile görevler bağımlılık seviyelerine ayrılır
3. **Paralel yürütme**: Aynı seviyedeki görevler `asyncio.gather()` ile paralel çalışır

**Örnek:**
```python
# Sorgu: "ASELS THYAO GARAN son fiyatları"
# Planning Agent 3 bağımsız görev oluşturur:
[
    Task(id=1, description="ASELS fiyatı", depends_on=[]),  # Bağımsız
    Task(id=2, description="THYAO fiyatı", depends_on=[]),  # Bağımsız
    Task(id=3, description="GARAN fiyatı", depends_on=[]),  # Bağımsız
]

# Execution plan: 1 seviye, 3 görev → hepsi paralel çalışır ⚡
# Sonuç: 15s → 5s (3x hızlanma)
```

**Bağımlılık Kuralları:**

**Bağımsız görevler** (paralel-güvenli):
- Farklı hisseler: `["ASELS fiyatı", "THYAO fiyatı", "GARAN fiyatı"]`
- Farklı varlık tipleri: `["Altın fiyatı", "Dolar kuru", "BIST100"]`
- Aynı şirket, farklı veri: `["ASELS finansalları", "ASELS teknik analiz"]`

**Bağımlı görevler** (sıralı):
- Ara sonra çek: `Task 2 depends_on: [1]`
- Topla sonra hesapla: `Task 3 depends_on: [1, 2]`
- Fiyat al → önceki dönem al → değişim hesapla: `Task 3 depends_on: [1, 2]`

**Konfigürasyon:**
```bash
PARALLEL_EXECUTION=true   # Paralel yürütme (önerilen)
PARALLEL_EXECUTION=false  # Sıralı yürütme (debug için)
```

### 📊 Terminal Chart Visualization

BorsaCI, plotext kütüphanesi ile terminal içinde renkli grafikler oluşturur:

**Özellikler:**
- **Candlestick (Mum) Grafikler**: OHLC verisi ile profesyonel grafikler
- **ANSI Renkli Çıktı**: Yeşil (bullish) ve kırmızı (bearish) mumlar
- **JSON + Markdown Parse**: MCP çıktıları otomatik parse edilir
- **LLM Dışında Generate**: Hallucination önleme için chart'lar LLM dışında oluşturulur

**Trigger Kelimeler:**
- "grafik", "mum grafik", "candlestick", "chart", "plot"

**Örnek:**
```
>> ASELS 1 haftalık mum grafik
```

### 💬 Conversation History

**Özellikler:**
- Session boyunca konuşma bağlamı korunur
- Follow-up sorular desteklenir
- `clear` komutu ile history sıfırlanır

**Örnek:**
```
>> ASELS hissesi hakkında bilgi ver
[Detaylı analiz...]

>> alayım mı?
[Önceki analizi kullanarak yanıt verir]

>> detaylandır
[Bağlamı koruyarak daha fazla detay]
```

### 🔄 Auto-Update System

**Özellikler:**
- GitHub commit-based otomatik güncelleme
- Her başlangıçta yeni versiyon kontrolü
- `git pull` + otomatik program restart
- `--skip-update` flag ile devre dışı bırakılabilir

**Davranış:**
```bash
uv run borsaci                  # Auto-update etkin
uv run borsaci --skip-update    # Update kontrolü yok
```

### 🔌 MCP Connection Lifecycle

**Özellikler:**
- Session-based persistent connection
- Context manager pattern (`async with agent:`)
- PydanticAI MCPServerStreamableHTTP (native MCP client)
- 30s connection timeout

**Avantajlar:**
- Her sorgu için yeni bağlantı açma/kapama maliyeti yok
- Tool listing cache edilir
- Daha hızlı yanıt süreleri

## 🛡️ Güvenlik Özellikleri

- **Global Step Limit**: Sonsuz döngülerden koruma (varsayılan: 20)
- **Per-Task Limit**: Görev başına maksimum deneme (varsayılan: 5)
- **Loop Detection**: Tekrar eden aksiyonları tespit
- **Error Recovery**: Graceful error handling
- **Timeout Management**: MCP bağlantı timeout'ları

## 📁 Proje Yapısı

```
borsaci/
├── src/
│   └── borsaci/
│       ├── agent.py          # Multi-agent orchestrator
│       ├── model.py          # PydanticAI agent factory
│       ├── mcp_tools.py      # FastMCP client wrapper
│       ├── prompts.py        # Türkçe system prompts
│       ├── schemas.py        # Pydantic models
│       ├── cli.py            # CLI entry point
│       └── utils/
│           ├── logger.py     # Rich-based logging
│           └── ui.py         # Terminal UI components
├── pyproject.toml            # Project config
├── .env.example              # Environment template
└── README.md
```

## 🔧 Teknoloji Stack

| Bileşen | Teknoloji | Neden? |
|---------|-----------|--------|
| **Framework** | PydanticAI 1.5.0+ | Type-safe, modern, MCP native |
| **LLM** | Google Gemini 2.5 Series | Pro: güçlü reasoning, Flash: hızlı tool calling |
| **API Gateway** | OpenRouter | Esnek model seçimi, cost-effective |
| **MCP Client** | MCPServerStreamableHTTP | PydanticAI native MCP client (30s timeout) |
| **MCP Server** | Borsa MCP | 43+ finansal araç (BIST, TEFAS, Kripto, Forex) |
| **CLI** | prompt-toolkit | Async REPL, conversation history |
| **Charts** | plotext 5.3+ | Terminal candlestick charts, ANSI colors |
| **Rendering** | Rich | Markdown + ANSI rendering, beautiful output |
| **Type System** | Pydantic v2 | Runtime validation |
| **Package Manager** | uv | Fast, reliable Python package management |
| **Auto-Update** | GitHub API + git | Commit-based auto-update with restart |

### Model Seçimi

| Agent | Model | Rationale |
|-------|-------|-----------|
| **Planning** | Gemini 2.5 Pro | Güçlü reasoning, karmaşık task decomposition |
| **Action** | Gemini 2.5 Flash | Hızlı tool calling, MCP entegrasyonu |
| **Validation** | Gemini 2.5 Flash | Basit validation, hızlı yanıt |
| **Answer** | Gemini 2.5 Flash | Kaliteli Türkçe, markdown formatting |

## 🧪 Development

### Debug Mode

```bash
uv run borsaci --debug
```

### Test Query

```python
from borsaci.agent import BorsaAgent
import asyncio

async def test():
    agent = BorsaAgent()
    await agent.mcp.initialize()
    result = await agent.run("ASELS hissesi hakkında bilgi ver")
    print(result)

asyncio.run(test())
```

## ⚠️ Sorumluluk Reddi

### 🔬 Araştırma ve Eğitim Projesi

Bu proje **tamamen araştırma ve eğitim amaçlıdır**. BorsaCI:

- 🎓 **Akademik bir çalışmadır**: Multi-agent AI sistemleri ve finansal veri entegrasyonu üzerine eğitim amaçlı bir proje
- 📚 **Öğrenme aracıdır**: PydanticAI, MCP protocol ve LLM tool calling kavramlarını öğrenmek için geliştirilmiştir
- 🧪 **Deneysel bir sistemdir**: Production kullanımı için tasarlanmamıştır
- 🔬 **Araştırma amaçlıdır**: AI agent mimarileri ve finansal veri işleme konularında araştırma yapmak için oluşturulmuştur

### ⚠️ Yatırım Tavsiyesi Değildir

**KESİNLİKLE UYARI:** BorsaCI sağlanan bilgiler:

- ❌ **Yatırım tavsiyesi DEĞİLDİR**
- ❌ **Finansal danışmanlık DEĞİLDİR**
- ❌ **Al-sat önerisi DEĞİLDİR**
- ❌ **Gerçek finansal kararlar için KULLANILMAMALIDIR**

### 🚨 AI Sistemlerinin Riskleri

**Önemli Teknik Uyarılar:**

1. **Hallucination Riski**: AI modelleri olmayan bilgileri uyduabilir, yanlış veya tutarsız yanıtlar üretebilir
2. **Veri Doğruluğu**: Veriler üçüncü parti kaynaklardan gelir ve gecikme veya hatalar içerebilir
3. **Yorumlama Hataları**: AI sistemleri verileri yanlış yorumlayabilir veya bağlamdan koparabilir
4. **Güncellik**: Veriler gerçek zamanlı olmayabilir, fiyatlar değişmiş olabilir
5. **Teknik Hatalar**: Yazılım hataları, API problemleri veya bağlantı sorunları yanıtları etkileyebilir

### 💼 Profesyonel Danışmanlık Gereklidir

**MUTLAKA:**
- 🏦 Yatırım kararlarınız için **lisanslı finansal danışmana** başvurun
- 📊 Profesyonel **yatırım uzmanı**ndan görüş alın
- ⚖️ Yasal ve vergi konularında **profesyonel destek** alın
- 🎯 Kendi **risk toleransınızı** ve **finansal hedeflerinizi** belirleyin

### 📜 Yasal Sorumluluk

Bu yazılımı kullanarak:
- Projenin **araştırma/eğitim amaçlı** olduğunu kabul edersiniz
- Verilen bilgilerin **yatırım tavsiyesi olmadığını** kabul edersiniz
- Finansal kararlarınızdan **kendi sorumlu** olduğunuzu kabul edersiniz
- Yazılımın **"OLDUĞU GİBİ"** sağlandığını ve **garanti verilmediğini** kabul edersiniz
- Kullanımdan kaynaklanan zararlardan **geliştiricilerin sorumlu olmadığını** kabul edersiniz

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🔗 Bağlantılar

- **Borsa MCP**: [github.com/saidsurucu/borsa-mcp](https://github.com/saidsurucu/borsa-mcp)
- **PydanticAI**: [ai.pydantic.dev](https://ai.pydantic.dev)
- **OpenRouter**: [openrouter.ai](https://openrouter.ai)
- **Dexter**: [github.com/virattt/dexter](https://github.com/virattt/dexter)

## 👨‍💻 Yazar

**Said Surucu**

- GitHub: [@saidsurucu](https://github.com/saidsurucu)

## 🙏 Teşekkürler

- **Dexter** ekibine multi-agent pattern ilhamı için
- **Pydantic** ekibine harika framework için
- **Z.AI** ekibine GLM-4.6 için
- **OpenRouter** ekibine esnek API gateway için

---

**⭐ Eğer projeyi beğendiyseniz, GitHub'da yıldız vermeyi unutmayın!**
