# Borsacı 📊

[![Star History Chart](https://api.star-history.com/svg?repos=saidsurucu/borsaci&type=date&legend=top-left)](https://www.star-history.com/#saidsurucu/borsaci&type=date&legend=top-left)

**Türk Finans Piyasaları için AI Agent**

> 🔬 **Araştırma Projesi** | 📚 **Eğitim Amaçlı** | ⚠️ **Yatırım Tavsiyesi Değildir**
>
> Bu proje **tamamen eğitim ve araştırma amaçlı** geliştirilmiştir. Gerçek finansal kararlar için kullanılmamalıdır.

Borsacı, Borsa MCP sunucusunu kullanarak BIST hisseleri, TEFAS fonları, kripto paralar, döviz kurları ve makro ekonomik verilere erişim sağlayan ve bu verileri anlamlandırmayı amaçlayan bir AI Agent'tır.

## 🌟 Özellikler

- **23 Finansal Araç**: Borsa MCP Unified API ile tam kapsamlı piyasa erişimi
- **Claude Skill**: Python'sız, model-agnostik kullanım için `skill/borsaci/` ([aşağıda](#-claude-skill-pythonsız-alternatif))
- **Multi-Agent Architecture**: Görev planlama, yürütme, doğrulama ve yanıt sentezleme
- **Paralel Görev Yürütme**: Dependency-aware parallelization ile 50-70% performans artışı
- **Terminal Chart Visualization**: plotext ile renkli candlestick (mum) grafikleri
- **Quant Alpha Backtest**: BIST OHLCV verisiyle trend/momentum/ICT sinyalleri, backtest metrikleri ve equity curve
- **Conversation History**: Follow-up soru desteği ve konuşma bağlamı yönetimi
- **Markdown Rendering**: Rich formatlanmış terminal çıktısı
- **Auto-Update System**: GitHub commit-based otomatik güncelleme
- **Türkçe Native**: Tamamen Türkçe komutlar ve çıktılar
- **Type-Safe**: PydanticAI ile güvenli ve IDE-friendly geliştirme
- **Güçlü LLM**: Google Gemini 3 Series (Pro + Flash)
- **Ücretsiz Kullanım**: Google OAuth ile ücretsiz Gemini API erişimi
- **Alternatif**: OpenRouter ile ücretli API kullanımı (fallback)

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

## 🧩 Claude Skill (Python'sız Alternatif)

Borsacı'nın piyasa uzmanlığı, `skill/borsaci/` altında **saf markdown bir Claude Skill** olarak da
paketlenmiştir. Kod, LLM sağlayıcısı veya API anahtarı gerektirmez — modelin kendisi (Claude Code,
claude.ai veya skill + MCP destekleyen herhangi bir ajan) Borsa MCP araçlarını doğrudan kullanır.

### En kolay yol: ajana kurdur

Claude Code'a (veya benzer bir ajana) şunu söylemen yeterli:

> Şu skill'i kur: https://github.com/saidsurucu/borsaci/tree/master/skill/borsaci
> Gerekli MCP sunucusu: https://borsa.surucu.dev/mcp

Ajan skill dosyalarını indirip `~/.claude/skills/borsaci/` altına yerleştirir ve MCP sunucusunu ekler.

### Elle kurulum

```bash
# 1. Borsa MCP'yi ekle (skill'in tek veri kaynağı)
claude mcp add --transport http borsa https://borsa.surucu.dev/mcp

# 2. Skill'i kur
cp -r skill/borsaci ~/.claude/skills/
```

Sonrasında "ASELS son fiyatı", "GARAN'ı buffett gibi analiz et", "altın mı BIST mi kazandırdı"
gibi sorular skill'i tetikler.

| | Python uygulaması (`uv run borsaci`) | Claude Skill (`skill/borsaci/`) |
|---|---|---|
| Çalıştırma | Kendi ajan döngüsü (PydanticAI) | Host ajanın kendi döngüsü |
| Model | Gemini 3 (Google OAuth / OpenRouter) | Host'un modeli, model-agnostik |
| Kurulum | Python + uv + kimlik doğrulama | Klasörü kopyala |
| Grafik | Terminalde plotext mum grafiği | OHLC tablosu + ortam destekliyorsa görsel |

İkisi bağımsızdır ve senkron tutulmaz. Ayrıntılar: [`skill/borsaci/README.md`](skill/borsaci/README.md)

## 🚀 Kurulum

### 🐳 Docker ile Kurulum (Önerilen)

Docker kullanarak BorsaCI'yi hızlıca çalıştırabilirsiniz:

```bash
# 1. Repository'i klonlayın
git clone https://github.com/saidsurucu/borsaci.git
cd borsaci

# 2. .env dosyası oluşturun
cat > .env << EOF
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
EOF

# 3. Docker Compose ile çalıştırın
docker-compose run --rm borsaci
```

**Detaylı Docker kullanım kılavuzu için**: [DOCKER.md](DOCKER.md)

### Manuel Kurulum

#### Gereksinimler

* **Python Kurulumu:** Sisteminizde Python 3.11 veya üzeri kurulu olmalıdır. Kurulum sırasında "**Add Python to PATH**" (Python'ı PATH'e ekle) seçeneğini işaretlemeyi unutmayın. [Buradan](https://www.python.org/downloads/) indirebilirsiniz.
* **Git Kurulumu (Windows):** Bilgisayarınıza [git](https://git-scm.com/downloads/win) yazılımını indirip kurun. "Git for Windows/x64 Setup" seçeneğini indirmelisiniz.
* **`uv` Kurulumu:**
    * **Windows Kullanıcıları (PowerShell):** Bir CMD ekranı açın ve bu kodu çalıştırın: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
    * **Mac/Linux Kullanıcıları (Terminal):** Bir Terminal ekranı açın ve bu kodu çalıştırın: `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Microsoft Visual C++ Redistributable (Windows):** Bazı Python paketlerinin doğru çalışması için gereklidir. [Buradan](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) indirip kurun.
* **Node.js (Opsiyonel, Google OAuth için):** Google OAuth kullanmak için Node.js gereklidir. [Buradan](https://nodejs.org/) indirip kurun.
* **Gemini CLI (Önerilen, ÜCRETSİZ):** `npm install -g @google/gemini-cli` ile yükleyin ve `gemini` komutuyla bir kez giriş yapın
* **VEYA** OpenRouter kredisi satın alın ve API anahtarı oluşturun ([API anahtarı](https://openrouter.ai/keys))

#### Adım Adım

Terminal/CMD ekranını açın.

```bash
# 1. Repository'i klonlayın
git clone https://github.com/saidsurucu/borsaci.git
cd borsaci

# Daha önce indirildiyse güncelleme için
git pull

# 2. Dependencies'i yükleyin
uv sync

# 3a. ÖNERİLEN: Google OAuth (ÜCRETSİZ)
npm install -g @google/gemini-cli  # Gemini CLI yükle
gemini                              # Bir kez giriş yap (browser açılır)
uv run borsaci                      # Otomatik olarak Gemini CLI credentials kullanır

# 3b. ALTERNATİF: OpenRouter (Ücretli)
uv run borsaci
# İlk çalıştırmada OpenRouter API key'iniz sorulacak
```

**Önerilen Yöntem:** Gemini CLI ile Google OAuth kullanın - tamamen **ÜCRETSİZ**!

**Not:** BorsaCI önce Google OAuth credentials (`~/.gemini/oauth_creds.json`) arar. Bulamazsa OpenRouter API key sorar.

#### Environment Variables (.env)

```bash
# Provider Seçimi (Google OAuth önerilir - ÜCRETSİZ)
# Google OAuth: ~/.gemini/oauth_creds.json otomatik kullanılır
# OpenRouter: OPENROUTER_API_KEY gerektirir

# Sadece OpenRouter kullanıyorsanız zorunlu
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

**Provider Seçimi:**
- **Google OAuth (Önerilen)**: ÜCRETSİZ! Gemini CLI credentials kullanır
  - Kurulum: `npm install -g @google/gemini-cli && gemini`
  - Credentials: `~/.gemini/oauth_creds.json` → `~/.borsaci/credentials/google.json`
- **OpenRouter (Alternatif)**: Ücretli API, `OPENROUTER_API_KEY` gerektirir
  - İlk çalıştırmada otomatik sorulur

**Not:**
- `PARALLEL_EXECUTION=true` ile 50-70% performans artışı elde edilir
- Timeout değerleri: Planning (300s), Action (300s), Answer (300s)

## 💡 Kullanım

### İlk Çalıştırma

Borsacı ilk kez çalıştırıldığında API key'inizi soracaktır:

```bash
$ uv run borsaci

╔══════════════════════════════════════════════════════════╗
║                     BORSACI                              ║
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

**Quant Alpha / Backtest Sorguları:**
```
>> ASELS için alpha backtest yap ve grafiğini göster

>> THYAO hissesinde ICT likidite süpürmesi ve fair value gap ile tahmin üret

>> GARAN 5 yıllık algoritmik trading backtest sonuçlarını göster
```

Bu sorgularda BorsaCI mevcut `get_historical_data` OHLCV verisini kullanır ve lokal Python motoruyla
long-only BIST varsayımı altında backtest üretir. Rapor; alpha getirisi, al-tut karşılaştırması,
Sharpe, maksimum düşüş, yön tahmini isabeti, işlem sayısı ve terminal equity curve içerir.
Örnek doğrulama sonuçları için: [docs/quant_alpha_backtest.md](docs/quant_alpha_backtest.md)

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

Borsacı, **Dexter** tarzı multi-agent pattern kullanır ve modern özelliklerle güçlendirilmiştir:

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

**Araç Seçimi (Unified API):**
- Şirket araması → `search_symbol`
- Finansal tablo → `get_financial_statements`
- Fiyat bilgisi → `get_quick_info`, `get_historical_data`
- Fon araması → `get_fund_data`, `screen_funds`
- Kripto fiyat → `get_crypto_market`
- Döviz/Emtia → `get_fx_data`

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
- **OpenRouter** ekibine esnek API gateway için

---

**⭐ Eğer projeyi beğendiyseniz, GitHub'da yıldız vermeyi unutmayın!**
