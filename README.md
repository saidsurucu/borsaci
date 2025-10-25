# BorsaCI 📊

**Türk Finans Piyasaları için AI Agent**

BorsaCI, Borsa MCP sunucusunu kullanarak BIST hisseleri, TEFAS fonları, kripto paralar, döviz kurları ve makro ekonomik verilere erişim sağlayan akıllı bir finansal asistanıdır.

## 🌟 Özellikler

- **43 Finansal Araç**: Borsa MCP ile entegre tam kapsamlı piyasa erişimi
- **Multi-Agent Architecture**: Görev planlama, yürütme, doğrulama ve yanıt sentezleme
- **Türkçe Native**: Tamamen Türkçe komutlar ve çıktılar
- **Type-Safe**: PydanticAI ile güvenli ve IDE-friendly geliştirme
- **Güçlü LLM**: GLM-4.6:exacto ile yüksek doğruluklu tool calling
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

# Agent konfigürasyonu
MAX_STEPS=20
MAX_STEPS_PER_TASK=5
```

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

```
>> ASELS hissesinin son çeyrek gelir büyümesi nedir?

>> En iyi performans gösteren 5 A tipi fonu listele

>> Bitcoin TRY fiyatı ve son 24 saatteki değişim ne?

>> Teknoloji sektöründeki şirketleri karşılaştır

>> Son enflasyon rakamları ve EUR/TRY kuru nedir?
```

### Komutlar

- `exit`, `quit`, `çık` - Programdan çık
- `help`, `yardım` - Yardım göster
- `tools`, `araçlar` - Mevcut araçları listele
- `clear` - Ekranı temizle

## 🏗️ Mimari

BorsaCI, **Dexter** tarzı multi-agent pattern kullanır:

### 1. Planning Agent
Kullanıcı sorgusunu atomik görevlere ayırır.

**Örnek:**
```
Sorgu: "Son çeyrekte bankaların karlılığını karşılaştır"

Görevler:
1. Finans sektöründe bankaları ara
2. Her banka için Q4 gelir tablosunu al
3. Net kar marjlarını hesapla
```

### 2. Action Agent
Her görev için uygun Borsa MCP aracını seçer ve çalıştırır.

**Araç Seçimi:**
- Şirket araması → `search_bist_companies`
- Finansal tablo → `get_company_financials`
- Fon araması → `search_funds`

### 3. Validation Agent
Görevin tamamlanıp tamamlanmadığını kontrol eder.

**Kriterler:**
- Yeterli veri toplandı mı?
- Kurtarılamaz hata oluştu mu?
- Scope dışında mı?

### 4. Answer Agent
Toplanan verileri sentezleyerek kapsamlı Türkçe yanıt oluşturur.

**Format:**
- Veri odaklı analiz
- Sayılarla desteklenmiş
- Kaynak belirtme
- Yatırım tavsiyesi uyarısı

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
| **Framework** | PydanticAI | Type-safe, modern, MCP native |
| **LLM** | GLM-4.6:exacto | Yüksek tool calling doğruluğu |
| **API Gateway** | OpenRouter | Esnek model seçimi, cost-effective |
| **Tools** | FastMCP Client | Borsa MCP entegrasyonu |
| **CLI** | prompt-toolkit | Rich terminal deneyimi |
| **Logging** | Rich | Renkli ve güzel formatlanmış çıktı |
| **Type System** | Pydantic v2 | Runtime validation |

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

**ÖNEMLİ:** BorsaCI sadece bilgilendirme amaçlıdır. Sağlanan bilgiler:

- ❌ Yatırım tavsiyesi değildir
- ❌ Finansal danışmanlık değildir
- ❌ Al-sat önerisi değildir

Yatırım kararlarınızı vermeden önce mutlaka lisanslı bir finansal danışmana başvurunuz. AI sistemleri hata yapabilir (hallucination), verileri yanlış yorumlayabilir.

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
