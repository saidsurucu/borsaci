# Antigravity CLI ile Borsacı (Windows / PowerShell)

Depodaki `skill/borsaci/`, Antigravity CLI'nin kendi modelini ve MCP araç
döngüsünü kullanabilir. Python, uv, OpenRouter anahtarı veya eski Gemini CLI
OAuth dosyası bu kullanım için gerekli değildir. Antigravity'nin kendi oturumu
ve plan/kota koşulları geçerlidir.

Bu yol, `uv run borsaci` ile çalışan Python uygulamasından bağımsızdır.
Python OAuth kodunu uyarlamaz ve `src/borsaci/quant_alpha.py` içindeki backtest
işlevlerini kendiliğinden çalıştırmaz.

## 1. Ön koşullar

- Windows üzerinde kurulu ve oturumu açılmış Antigravity CLI (`agy`).
- Bu deponun yerel kopyası ve `https://borsa.surucu.dev/mcp` adresine ağ erişimi.

PowerShell'i deponun kökünde açın; yönetici olarak çalıştırmanız gerekmez.
`agy` bulunamıyorsa Antigravity kurulumunu/PATH ayarını kontrol edin ve yeni
bir terminal açın. Antigravity'nin grafik IDE uygulaması ile CLI aynı arayüz değildir.

## 2. Skill'i projeye ekleyin

Antigravity CLI, proje skill'lerini `.agents/skills/` altında bulur.
Aşağıdaki komutlar mevcut bir Borsacı skill'inin üzerine yazmaz:

```powershell
if (Test-Path -LiteralPath '.agents/skills/borsaci') {
    throw 'Borsaci skill zaten kurulu; mevcut dosyalari inceleyin.'
}
New-Item -ItemType Directory -Path '.agents/skills' -Force | Out-Null
Copy-Item -LiteralPath 'skill/borsaci' -Destination '.agents/skills/borsaci' -Recurse
```

`references/` klasörü de kopyalanmalıdır. Skill'i güncellerken kaynak olarak
`skill/borsaci/` klasörünü kullanın; iki ayrı skill kopyasını geliştirmeyin.

## 3. Borsa MCP bağlantısını ekleyin

Örnek dosya: [`examples/antigravity/mcp_config.json`](../examples/antigravity/mcp_config.json).

Projenizde henüz `.agents/mcp_config.json` yoksa:

```powershell
if (Test-Path -LiteralPath '.agents/mcp_config.json') {
    throw 'MCP ayari zaten var; borsa kaydini mevcut mcpServers nesnesine ekleyin.'
}
Copy-Item -LiteralPath 'examples/antigravity/mcp_config.json' -Destination '.agents/mcp_config.json'
```

Dosya zaten varsa diğer sunucuları koruyarak `mcpServers` nesnesine şu kaydı ekleyin:

```json
"borsa": {
  "serverUrl": "https://borsa.surucu.dev/mcp"
}
```

Bu parça tek başına JSON dosyası değildir; tam örnek için bağlantıdaki dosyayı kullanın.
Eski `borsamcp.fastmcp.app` adresini kullanmayın.

Antigravity CLI ayrıca tüm projeler için `~/.gemini/config/mcp_config.json`
konumunu destekler. Aynı sunucu zaten global olarak tanımlıysa proje kaydı
eklemek yerine mevcut bağlantıyı `/mcp` ile kontrol edin.

## 4. Yeni oturumda doğrulayın

Deponun kökünde yeni bir Antigravity CLI oturumu başlatın:

```powershell
agy
```

Antigravity mesaj alanında `/mcp` yazın ve `borsa` sunucusunun bağlı olduğunu
kontrol edin. Sonra şu soruyu gönderin:

> Borsacı skill'ini kullanarak ASELS'in son fiyatını getir. Verinin tarihini ve kaynağını belirt.

Başarılı doğrulamada:

- Ajan `.agents/skills/borsaci/SKILL.md` dosyasını okur.
- `borsa/get_quote` aracını çağırır (`symbol="ASELS"`, `market="bist"`).
- Türkçe yanıtta veri kaynağı, para birimi ve verinin tarihi yer alır.

Sunucunun yanıt zamanı ile fiyatın işlem/kapanış zamanı aynı olmayabilir.
Hafta sonu alınan yanıtı yeni bir işlem günü fiyatı olarak yorumlamayın;
araç gerçek işlem zamanını vermiyorsa bu belirsizliği belirtin.

MCP bağlı değilse veya araç hata veriyorsa modelden fiyat tahmin etmesini istemeyin.
`/mcp` bağlantı durumunu ve ağ erişimini kontrol edin. Güncel araç adları ve
parametrelerinde canlı MCP şeması esas alınır.

## Doğrulama kapsamı

15 Kasım 2026 tarihinde Windows / PowerShell üzerinde Antigravity CLI **1.5.9**
ile skill'in okunması ve `borsa/get_quote` çağrısıyla ASELS yanıtı alınması
kullanıcı ekran görüntüsünde doğrulandı. Ayrı bir protokol kontrolünde BorsaMCP
**4.0.3** sunucusundan **23 araç** listelendi. Bu kontrol, tüm analiz/tarama
senaryolarının veya Python uygulamasının doğrulandığı anlamına gelmez.

## Resmî Antigravity belgeleri

- [Gemini CLI'den geçiş: skill ve MCP konumları](https://antigravity.google/docs/cli/gcli-migration)
- [MCP yapılandırması ve /mcp](https://antigravity.google/docs/mcp)
- [Antigravity kimlik doğrulaması](https://antigravity.google/docs/install?tab=cli)
