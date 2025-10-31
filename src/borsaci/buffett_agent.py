"""Warren Buffett style investment analysis agent"""

from typing import Optional, Any
import os
import sys

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import RunUsage
from pydantic_ai.mcp import CallToolFunc, ToolResult

from .model import get_action_model
from .prompts import get_warren_buffett_prompt, get_data_collection_prompt
from .mcp_tools import BorsaMCP
from .utils.logger import Logger

logger = Logger()


# MCP Tool name → User-friendly message mapping
MCP_TOOL_MESSAGES = {
    "find_ticker_code": "🔍 Şirket ticker kodu aranıyor...",
    "calculate_buffett_value_analysis": "🧮 Buffett analizi yapılıyor (OE, DCF, Güvenlik Marjı)...",
    "get_sirket_profili": "🏢 Şirket profili getiriliyor...",
    "get_bilanco": "📋 Bilanço verileri alınıyor...",
    "get_kar_zarar_tablosu": "💰 Gelir tablosu getiriliyor...",
    "get_nakit_akisi_tablosu": "💸 Nakit akışı verileri alınıyor...",
    "get_hizli_bilgi": "💵 Güncel fiyat bilgisi alınıyor...",
    "get_analist_tahminleri": "📊 Analist tahminleri getiriliyor...",
}


async def buffett_process_tool_call(
    ctx: RunContext[Any],
    call_tool: CallToolFunc,
    name: str,
    tool_args: dict[str, Any],
) -> ToolResult:
    """
    Process tool calls with user-friendly progress messages.

    Shows real-time progress for MCP tools and Python calculation tools.
    In debug mode, also shows tool parameters.
    """
    # Show user-friendly message for MCP tools
    if name in MCP_TOOL_MESSAGES:
        logger.log_info(MCP_TOOL_MESSAGES[name])

    # Debug mode: Show tool name and parameters
    if "--debug" in sys.argv:
        print(f"[DEBUG] Tool: {name}")
        if tool_args:
            print(f"[DEBUG] Args: {tool_args}")

    # Execute the tool
    return await call_tool(name, tool_args)


class BuffettAgent:
    """
    Warren Buffett investment analysis agent.

    Self-contained agent that performs complete Buffett-style analysis:
    1. Circle of Competence (Yeterlilik Dairesi)
    2. Moat Analysis (Rekabet Avantajı)
    3. Owner Earnings (Sahip Kazançları)
    4. Intrinsic Value & Safety Margin (İçsel Değer & Güvenlik Marjı)
    5. Buy/Pass/Watch Decision (Karar)
    6. Position Sizing (Pozisyon Önerisi)

    Architecture (Two-Phase):
    - Phase 1: Data Collector Agent (MCP tool calling, no structured output)
    - Phase 2: Analysis Agent (Structured output, no tool calling)
    - Model: Gemini 2.5 Flash (or configurable via BUFFETT_MODEL)
    """

    def __init__(self, mcp_client: BorsaMCP):
        """
        Initialize BuffettAgent with two-phase architecture.

        Args:
            mcp_client: BorsaMCP client for accessing financial data
        """
        # Create new MCP client with process_tool_call for progress messages
        self.mcp = BorsaMCP(
            server_url=mcp_client.server_url,
            process_tool_call=buffett_process_tool_call
        )

        # Model selection (allow override via env)
        model = os.getenv("BUFFETT_MODEL", get_action_model())

        # Phase 1: Data Collection Agent
        # - Uses MCP tools to gather financial data
        # - calculate_buffett_value_analysis MCP tool does all calculations
        # - No structured output - returns YAML with raw data + calculations
        self.data_collector = Agent(
            model=model,
            system_prompt=get_data_collection_prompt(),
            toolsets=[self.mcp],  # MCP tools (includes calculate_buffett_value_analysis)
            # No tools parameter - all calculations done by MCP tool
            # No output_type - free-form tool calling
            retries=3,
        )

        # Phase 2: Analysis Agent
        # - Analyzes collected data using Buffett framework
        # - Free-form markdown output (no structured constraint)
        # - No tool calling - pure analysis
        self.analyzer = Agent(
            model=model,
            system_prompt=get_warren_buffett_prompt(),
            # No toolsets - analysis only
            # No output_type - free-form markdown
            retries=3,
        )

    async def analyze(
        self,
        query: str,
        usage: Optional[RunUsage] = None
    ) -> str:
        """
        Perform Warren Buffett style investment analysis (Two-Phase).

        Process:
        Phase 1: Data Collection
        - Use data_collector agent to call MCP tools
        - Gather financial data (company profile, financials, price, etc.)
        - Return raw data as string

        Phase 2: Analysis
        - Use analyzer agent with collected data
        - Apply Buffett framework (moat, owner earnings, DCF, safety margin)
        - Return markdown-formatted analysis report

        Args:
            query: User's original query (e.g., "aselsanı analiz et")
            usage: Optional RunUsage for tracking

        Returns:
            Markdown-formatted analysis report (string)
        """
        import sys

        if "--debug" in sys.argv:
            print(f"[DEBUG] BuffettAgent analyzing query: {query}")

        # Initialize shared usage tracking
        if usage is None:
            usage = RunUsage()

        try:
            # ==========================================
            # PHASE 1: DATA COLLECTION
            # ==========================================
            if "--debug" in sys.argv:
                print("[DEBUG] Phase 1: Collecting financial data...")

            data_collection_prompt = f"""
Kullanıcı Sorusu: {query}

Lütfen yukarıdaki sorgu için finansal veri topla.
Tüm gerekli MCP araçlarını kullan (search, profile, financials, price).
"""

            data_result = await self.data_collector.run(
                data_collection_prompt,
                usage=usage,
            )

            # Extract collected data
            collected_data = data_result.output if hasattr(data_result, 'output') else str(data_result)

            if "--debug" in sys.argv:
                print(f"[DEBUG] Phase 1 completed. Data length: {len(collected_data)} chars")
                print("[DEBUG] Full collected data:")
                print("=" * 80)
                print(collected_data)
                print("=" * 80)

            # Check if data collection was successful
            if not collected_data or len(collected_data) < 100:
                raise ValueError("Veri toplama başarısız - yeterli veri toplanamadı")

            # ==========================================
            # PHASE 2: ANALYSIS
            # ==========================================
            if "--debug" in sys.argv:
                print("[DEBUG] Phase 2: Analyzing collected data with Buffett framework...")

            analysis_prompt = f"""
Aşağıdaki finansal veriler ve Python hesaplamaları toplandı:

{collected_data}

---

Yukarıdaki YAML verisini kullanarak Warren Buffett yatırım felsefesine göre analiz yap.
NOT: 'calculations' bölümündeki tüm hesaplamalar Python ile yapılmış (güvenilir).

GÖREV ADIMLARI:

1. **Yeterlilik Dairesi Değerlendirmesi**:
   - İş modeli anlaşılır mı?
   - Sektör dinamikleri tahmin edilebilir mi?
   - Güven skoru: 0.0-1.0

2. **Moat Analizi**:
   - Hangi rekabet avantajı türü? (Marka, Ağ Etkisi, Maliyet, Değişim Maliyeti, Düzenleyici)
   - Moat kalitesi: KAÇINILMAZ | GÜÇLÜ | ORTA | ZAYIF
   - Sürdürülebilirlik: Kaç yıl?

3. **Sahip Kazançları Hesaplama**:
   - Net Gelir + Amortisman - CapEx - İşletme Sermayesi Artışı
   - Owner Earnings Getirisi = OE / Piyasa Değeri
   - Hedef: >%10

4. **İçsel Değer (DCF) Hesaplama**:
   - Büyüme oranları: 1-5 yıl (max %15), 6-10 yıl (max %10), sonrası (%3-5)
   - İskonto oranı: Hazine + Risk Primi (min %10)
   - Terminal çarpan: 15x (kaliteli işler için)
   - Hesapla: İçsel Değer Per Share

5. **Güvenlik Marjı**:
   - İndirim = (İçsel Değer - Mevcut Fiyat) / İçsel Değer
   - Eşik: Harika işler %30, İyi işler %50

6. **KARAR**:
   - ✅ SATIN AL: Moat güçlü + Güvenlik marjı yeterli
   - 📊 İZLE: Güvenlik marjı yetersiz ama kaliteli
   - ❌ PAS: Zayıf moat veya anlaşılmaz

7. **Pozisyon Önerisi** (eğer SATIN AL ise):
   - Ekstrem güven: %25-50
   - Yüksek güven: %10-25
   - Standart güven: %5-10

8. **Uyarılar**:
   - Sektör riskleri
   - Türkiye özel riskler (döviz, politik, regülasyon)
   - Disclaimer: "Bu bir yatırım tavsiyesi değildir"

ÖNEMLİ:
- Spesifik sayılar kullan (%, TL, yıl)
- Her aşamayı Buffett prensipleri ile yorumla
- Belirsizlik varsa "PAS" öner
- Ham verileri raw_data alanına kaydet (debug için)
"""

            analysis_result = await self.analyzer.run(
                analysis_prompt,
                usage=usage,
            )

            if "--debug" in sys.argv:
                print("[DEBUG] Phase 2 completed")
                print(f"[DEBUG] Analysis length: {len(analysis_result.output)} chars")

            return analysis_result.output

        except Exception as e:
            if "--debug" in sys.argv:
                print(f"[DEBUG] BuffettAgent error: {e}")
                import traceback
                traceback.print_exc()

            # Return error message
            return f"""# ❌ Analiz Hatası

**Hata**: {str(e)}

Analiz tamamlanamadı. Lütfen tekrar deneyin veya farklı bir şirket seçin.

---
⚠️ Bu bir yatırım tavsiyesi değildir."""



# Standalone Python calculation functions
# These can be provided to LLM as tool descriptions, but calculations
# will be done by LLM reasoning + MCP data (not separate tool calls)

def calculate_owner_earnings_description() -> str:
    """
    Owner Earnings calculation formula for LLM.

    This is provided as guidance to the LLM, not as an executable tool.
    LLM will perform the calculation using MCP financial data.
    """
    return """
Owner Earnings Hesaplama:

Formula:
    Owner Earnings = Net Gelir
                    + Amortisman ve İtfalar
                    + Nakit Olmayan Giderler
                    - Bakım CapEx
                    - İşletme Sermayesi Artışı

Bakım CapEx Tahmini:
    - Son 7 yılın CapEx / Satış oranlarını incele
    - Satışların düz/düşük olduğu yılları belirle
    - O yılların CapEx ortalaması ≈ Bakım CapEx
    - Alternatif: CapEx'in %60-80'i bakım (sektöre göre)

Owner Earnings Getirisi:
    OE Getirisi = Owner Earnings / Piyasa Değeri
    Hedef: >%10 (minimum kabul edilebilir)

Örnek Hesaplama:
    Net Gelir: 1,000 milyon TL
    Amortisman: +200 milyon TL
    CapEx: -300 milyon TL (tahmini %70 bakım = 210 milyon TL)
    İşletme Sermayesi: -50 milyon TL
    → Owner Earnings = 1000 + 200 - 210 - 50 = 940 milyon TL

    Piyasa Değeri: 8,000 milyon TL
    → OE Getirisi = 940 / 8000 = 11.75% ✓ (>%10 hedefini geçti)
"""


def calculate_dcf_description() -> str:
    """
    DCF (Discounted Cash Flow) calculation formula for LLM - Fisher Etkisi metodolojisi.
    """
    return """
İçsel Değer (DCF) Hesaplama - Fisher Etkisi ile Reel DCF:

**ÖNEMLI**: Türkiye gibi yüksek enflasyon ortamlarında nominal ve reel değerleri karıştırmamak için Fisher Etkisi kullanılır.

Fisher Etkisi Formülü:
    rreal = (1 + r_nominal) / (1 + π) - 1 + risk_premium
    İçsel Değer = Σ(OE_real_t / (1+rreal)^t) + Terminal_Value / (1+rreal)^N
    Terminal_Value = OE_N × (1 + g_terminal_real) / (rreal - g_terminal_real)

**Parametreler (Ekim 2025 Türkiye):**

1. **Nominal Faiz Oranı (nominal_rate):**
   - 10 yıllık Türkiye tahvili: %30
   - Default: 0.30
   - Kaynak: Bloomberg, TCMB

2. **Beklenen Enflasyon (expected_inflation):**
   - TCMB beklentisi: %38
   - Default: 0.38
   - Kaynak: TCMB beklenti anketi, piyasa konsensüsü

3. **Risk Primi (risk_premium) - Moat Bazlı:**
   - KAÇINILMAZ moat: %8 (çok düşük risk)
   - GÜÇLÜ moat: %10 (default - düşük risk)
   - ORTA moat: %12 (orta risk)
   - ZAYIF moat: %15+ (yüksek risk)

4. **Reel Büyüme Oranı (growth_rate_real) - Enflasyon Üstü:**
   - KAÇINILMAZ moat: %4-5 (sürdürülebilir yüksek büyüme)
   - GÜÇLÜ moat: %3-4 (sağlam büyüme)
   - ORTA moat: %2-3 (orta büyüme)
   - ZAYIF moat: %0-2 (düşük büyüme)
   - Default: %3

5. **Terminal Reel Büyüme (terminal_growth_real):**
   - Matür ekonomi için reel GSYİH büyümesi
   - Türkiye: %2 (uzun vadeli ortalama)
   - Global: %2-2.5
   - Default: %2
   - ÖNEMLİ: Reel büyüme, enflasyon üstü büyümedir!

6. **Projeksiyon Süresi (forecast_years):**
   - Default: 5 yıl
   - Uzatma yalnızca çok yüksek görünürlük varsa

**Örnek Hesaplama (ASELS - GÜÇLÜ moat):**

1. Fisher Etkisi ile Reel WACC:
   ```
   r_nominal = %30 (10Y tahvil)
   π = %38 (enflasyon)
   risk_premium = %10 (GÜÇLÜ moat)

   rreal = (1.30 / 1.38) - 1 + 0.10
   rreal = 0.9420 - 1 + 0.10
   rreal = -0.058 + 0.10 = 0.042 (%4.2)
   ```

   **Not**: Reel faiz negatif (%−5.8) çünkü tahvil getirisi enflasyonun altında!

2. Reel Nakit Akışı Projeksiyonu:
   ```
   OE (çeyreklik): 700M TL → Yıllık: 2,800M TL (reel - bugünkü TL)
   Reel büyüme: %3 (enflasyon üstü)

   Yıl 1: 2,800 × 1.03 / 1.042^1 = 2,763M TL
   Yıl 2: 2,800 × 1.03^2 / 1.042^2 = 2,727M TL
   Yıl 3: 2,800 × 1.03^3 / 1.042^3 = 2,692M TL
   Yıl 4: 2,800 × 1.03^4 / 1.042^4 = 2,658M TL
   Yıl 5: 2,800 × 1.03^5 / 1.042^5 = 2,625M TL

   PV (5 yıl) = 13,465M TL
   ```

3. Terminal Value (Reel):
   ```
   OE_5 = 2,800 × 1.03^5 = 3,245M TL
   Terminal OE = 3,245 × 1.02 = 3,310M TL
   Terminal Value = 3,310 / (0.042 - 0.02) = 150,455M TL
   PV Terminal = 150,455 / 1.042^5 = 122,939M TL
   ```

4. Toplam İçsel Değer:
   ```
   İçsel Değer = 13,465 + 122,939 = 136,404M TL
   Hisse Sayısı: 240M
   İçsel Değer/Hisse = 136,404 / 240 = 568 TL
   ```

**Kritik Kurallar:**
- ✅ Owner Earnings REEL kabul edilir (bugünkü TL cinsinden)
- ✅ Büyüme oranları REEL (enflasyon üstü %0-5)
- ✅ İskonto oranı REEL (%4-6 tipik Türkiye için)
- ✅ Terminal büyüme REEL (%2 GSYİH)
- ❌ Nominal ve reel karıştırma - tutarsızlık yaratır!
- ⚠️ Negatif reel faiz normal (Türkiye'de tahviller enflasyonun altında)

**Neden Fisher Etkisi?**
- Enflasyon tutarlılığı: Hem pay hem payda reel
- Basitlik: Karmaşık enflasyon tahminleri gereksiz
- Doğruluk: Nominal/reel karışıklığını önler
- Türkiye gerçeği: Yüksek nominal oranları reel'e çevirir
"""


def calculate_moat_score_description() -> str:
    """
    Moat quality scoring guidelines for LLM.
    """
    return """
Rekabet Avantajı (Moat) Skorlama:

Moat Türleri (kombinasyonlar mümkün):

1. Marka Gücü (Brand Power):
   - Müşteriler markaya sadık
   - Fiyat artırma gücü
   - Örnekler: Coca-Cola, Apple, Ülker, Arçelik

2. Ağ Etkisi (Network Effects):
   - Kullanıcı arttıkça değer artar
   - Rakip girmesi zorlaşır
   - Örnekler: Visa, Facebook, Garanti BBVA (şube ağı)

3. Maliyet Avantajı (Cost Advantage):
   - Sektörün en düşük maliyetli üreticisi
   - Ölçek ekonomisi
   - Örnekler: BİM, A101, Walmart

4. Değişim Maliyeti (Switching Costs):
   - Müşterin başka ürüne geçmesi pahalı
   - Lock-in etkisi
   - Örnekler: Microsoft, SAP, bankalar (maaş hesabı)

5. Düzenleyici Engel (Regulatory Barriers):
   - Lisans/izin gereken sektörler
   - Örnekler: Havayolları (slot), telekom (frekans)

Moat Kalite Seviyeleri:

KAÇINILMAZ (20+ yıl):
- Dominantlığı tehdit edemezsiniz
- Çok güçlü marka + ağ etkisi
- Örnekler: Coca-Cola, See's Candies
- BIST'te nadir

GÜÇLÜ (10-20 yıl):
- Güçlü engeller, zorlu rekabet
- Teknoloji liderliği + marka
- Örnekler: Apple, Google
- BIST: Aselsan, Koç Holding şirketleri

ORTA (5-10 yıl):
- Bazı avantajlar ama tehdit altında
- Rekabet artabilir
- BIST: Orta ölçekli endüstriyel şirketler

ZAYIF (<5 yıl):
- Zayıf engeller, fiyat rekabeti
- Commodity ürünler
- BIST: Çoğu küçük şirket

Değerlendirme Kriterleri:
1. Fiyatlama gücü var mı? (enflasyonu aşan fiyat artışı)
2. Pazar payı istikrarlı veya artıyor mu?
3. Yeni rakip girişi ne kadar zor?
4. Müşteri sadakati ne kadar güçlü?
5. Kar marjları sektör ortalamasının üstünde mi?
"""


def calculate_safety_margin_description() -> str:
    """
    Safety margin calculation and thresholds.
    """
    return """
Güvenlik Marjı (Margin of Safety) Hesaplama:

Formula:
    Güvenlik Marjı = (İçsel Değer - Mevcut Fiyat) / İçsel Değer

Buffett Eşikleri (Moat Kalitesine Göre):

1. Harika İşler (KAÇINILMAZ moat):
   - Minimum indirim: %30
   - Mantık: Moat o kadar güçlü ki, %30 indirim yeterli güvenlik sağlar
   - Örnekler: Coca-Cola (%30-40 indirimde al)

2. İyi İşler (GÜÇLÜ moat):
   - Minimum indirim: %50
   - Mantık: Güçlü ama belirsizlik daha fazla
   - Örnekler: Bank of America (%50+ indirimde al)

3. Ortalama İşler (ORTA moat):
   - Minimum indirim: %60-70
   - Mantık: Risk yüksek, büyük indirim gerekli

4. Zayıf İşler (ZAYIF moat):
   - Önerisi: ALMA
   - Buffett: "Hiçbir fiyatta ilgilenmem"

Karar Matrisi:

İndirim < Eşik:
→ "İZLE" kararı (henüz yeterli güvenlik yok)

İndirim ≥ Eşik:
→ "SATIN AL" kararı (yeterli güvenlik marjı var)

İndirim negatif (mevcut fiyat > içsel değer):
→ "PAS" kararı (aşırı değerli)

Özel Durumlar:
- Türkiye pazarında belirsizlik yüksek → Eşikleri %10-15 artır
- Döviz riski yüksekse → İskonto oranına yansıt (DCF'de)
- Politik risk varsa → Moat sürdürülebilirliğini düşür
"""


def calculate_position_size_description() -> str:
    """
    Position sizing recommendations based on Kelly Criterion.
    """
    return """
Pozisyon Büyüklüğü (Position Sizing) Önerileri:

Modifiye Kelly Kriteri:
    Pozisyon % = (Beklenen Getiri - Risksiz Oran) / Varyans × Güven × Güvenlik

Buffett'ın Gerçek Pozisyon Seviyeleri:

1. EKSTREM GÜVEN (%25-50):
   - Moat: KAÇINILMAZ
   - Güvenlik Marjı: >%40
   - Yönetim: Mükemmel
   - Örnekler: Apple (%48), Coca-Cola (%43)
   - Beklenen Getiri: >%30 yıllık
   - Kazanma Olasılığı: >%90

2. YÜKSEK GÜVEN (%10-25):
   - Moat: GÜÇLÜ
   - Güvenlik Marjı: %30-40
   - Yönetim: İyi
   - Örnekler: Bank of America (%15), Wells Fargo (%24)
   - Beklenen Getiri: %20-30 yıllık
   - Kazanma Olasılığı: %80-90

3. STANDART GÜVEN (%5-10):
   - Moat: GÜÇLÜ veya ORTA
   - Güvenlik Marjı: %20-30
   - Yönetim: Kabul edilebilir
   - Diğer Berkshire holdingleri
   - Beklenen Getiri: %15-20 yıllık
   - Kazanma Olasılığı: %70-80

4. BAŞLANGIÇ POZİSYONU (%1-5):
   - Tez testi (henüz tam güven yok)
   - Yavaş biriktirme stratejisi
   - Belirsizlik yüksek
   - Öğrenme aşaması

KARAR AĞACI:

if Moat == "KAÇINILMAZ" and İndirim > %40:
    → %25-50 (ekstrem güven)

elif Moat == "GÜÇLÜ" and İndirim > %30:
    → %10-25 (yüksek güven)

elif Moat == "GÜÇLÜ" and İndirim > %20:
    → %5-10 (standart güven)

elif Moat == "ORTA" and İndirim > %50:
    → %5-10 (temkinli)

else:
    → "İZLE" veya "PAS" (pozisyon açma)

Türkiye Pazarı İçin Düzeltmeler:
- Volatilite yüksek → Pozisyon büyüklüğünü %30-40 azalt
- Likidite düşük → Maksimum pozisyon %15-20 ile sınırla
- Döviz riski → Portföy çeşitlendirmesi kritik

Örnek Öneri Formatı:
"Portföyün %10-15'i (yüksek güven, güçlü moat, yeterli güvenlik marjı)"
"""


# =============================================================================
# Python Calculation Tools for Data Collection Agent
# =============================================================================

# NOTE: Python calculation functions moved to Borsa MCP
# All Buffett value calculations now performed by calculate_buffett_value_analysis MCP tool
# This includes:
#   - Owner Earnings calculation
#   - OE Yield calculation
#   - DCF (Fisher Etkisi) valuation
#   - Safety Margin calculation
#
# The MCP tool provides a single atomic operation that:
#   1. Fetches all required financial data (bilanco, kar_zarar, nakit_akisi, hizli_bilgi)
#   2. Performs all 4 calculations with consistent data
#   3. Returns comprehensive buffett_analysis result
#
# Benefits:
#   - Single MCP call (reduced latency)
#   - Atomic transaction (data consistency)
#   - Centralized maintenance (single source of truth)
#   - Reusable across different agents/projects
