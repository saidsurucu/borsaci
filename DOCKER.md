# 🐳 BorsaCI Docker Kullanım Kılavuzu

Bu kılavuz, BorsaCI uygulamasını Docker ile nasıl çalıştıracağınızı açıklar.

## 📋 Gereksinimler

-   **Docker**: [Docker Desktop](https://www.docker.com/products/docker-desktop) yüklü olmalı
-   **Docker Compose**: Docker Desktop ile birlikte gelir
-   **OpenRouter API Key**: [OpenRouter](https://openrouter.ai/keys) hesabı ve API key

## 🚀 Hızlı Başlangıç

### 1. Environment Dosyasını Hazırlayın

`.env` dosyası oluşturun ve OpenRouter API key'inizi ekleyin:

```bash
# .env dosyası oluştur
cat > .env << EOF
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
HTTP_REFERER=https://borsaci.app
X_TITLE=BorsaCI
BORSA_MCP_URL=https://borsamcp.fastmcp.app/mcp
MAX_STEPS=20
MAX_STEPS_PER_TASK=5
PARALLEL_EXECUTION=true
EOF
```

**Veya** `.env.docker.example` dosyasını kopyalayın:

```bash
cp .env.docker.example .env
# Ardından .env dosyasını düzenleyip API key'inizi ekleyin
```

### 2. Docker Compose ile Çalıştırın

```bash
# Container'ı build edin ve başlatın
docker-compose up -d

# Interactive mode'da çalıştırın (önerilen)
docker-compose run --rm borsaci

# Veya detached container'a attach olun
docker attach borsaci
```

### 3. Kullanım

Container başlatıldığında BorsaCI interactive REPL açılacaktır:

```
╔══════════════════════════════════════════════════════════╗
║                     BORSACI                              ║
╚══════════════════════════════════════════════════════════╝

✅ BorsaCI hazır! (MCP bağlantısı kuruldu)

>> ASELS hissesi hakkında bilgi ver
```

## 🛠️ Docker Komutları

### Container Yönetimi

```bash
# Container'ı başlat (detached mode)
docker-compose up -d

# Container'ı durdur
docker-compose stop

# Container'ı kaldır
docker-compose down

# Container loglarını görüntüle
docker-compose logs -f

# Container içinde shell aç
docker-compose exec borsaci /bin/bash
```

### Image Yönetimi

```bash
# Image'ı yeniden build et
docker-compose build

# Image'ı build et (cache kullanmadan)
docker-compose build --no-cache

# Kullanılmayan image'ları temizle
docker image prune -a
```

### Interactive Mode

```bash
# Tek seferlik interactive session
docker-compose run --rm borsaci

# Debug mode ile çalıştır
docker-compose run --rm borsaci uv run borsaci --debug

# Auto-update olmadan çalıştır
docker-compose run --rm borsaci uv run borsaci --skip-update
```

## 🔧 Konfigürasyon

### Environment Variables

Docker container'ı aşağıdaki environment variables'ı destekler:

| Variable             | Varsayılan                         | Açıklama                     |
| -------------------- | ---------------------------------- | ---------------------------- |
| `OPENROUTER_API_KEY` | -                                  | OpenRouter API key (zorunlu) |
| `HTTP_REFERER`       | `https://borsaci.app`              | OpenRouter app referrer      |
| `X_TITLE`            | `BorsaCI`                          | OpenRouter app başlığı       |
| `BORSA_MCP_URL`      | `https://borsamcp.fastmcp.app/mcp` | MCP server URL               |
| `MAX_STEPS`          | `20`                               | Global maksimum adım sayısı  |
| `MAX_STEPS_PER_TASK` | `5`                                | Görev başına maksimum adım   |
| `PARALLEL_EXECUTION` | `true`                             | Paralel görev yürütme        |

### docker-compose.yml Özelleştirme

`docker-compose.yml` dosyasını ihtiyaçlarınıza göre düzenleyebilirsiniz:

```yaml
services:
    borsaci:
        # Port mapping (eğer web interface eklerseniz)
        ports:
            - '8000:8000'

        # Memory limitleri
        mem_limit: 512m
        mem_reservation: 256m

        # CPU limitleri
        cpus: '0.5'

        # Restart policy
        restart: always # Her zaman yeniden başlat
```

## 📦 Dockerfile Detayları

BorsaCI Dockerfile'ı şu özellikleri içerir:

-   **Base Image**: `python:3.11-slim` (minimal boyut)
-   **Package Manager**: `uv` (hızlı Python paket yönetimi)
-   **System Dependencies**: `git` (auto-update için)
-   **Working Directory**: `/app`
-   **Volume Mount**: `.env` dosyası için

### Multi-stage Build (Opsiyonel)

Daha küçük image boyutu için multi-stage build kullanabilirsiniz:

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./
RUN uv sync --frozen

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "borsaci.cli"]
```

## 🐛 Troubleshooting

### API Key Hatası

```
⚠️  Uyarı: OPENROUTER_API_KEY bulunamadı!
```

**Çözüm**: `.env` dosyasının doğru konumda olduğundan ve API key'in doğru girildiğinden emin olun.

```bash
# .env dosyasını kontrol et
cat .env | grep OPENROUTER_API_KEY

# Container'daki environment variables'ı kontrol et
docker-compose exec borsaci env | grep OPENROUTER
```

### MCP Connection Hatası

```
❌ Borsa MCP bağlantısı kurulamadı
```

**Çözüm**: Network bağlantısını ve MCP server URL'ini kontrol edin.

```bash
# Container içinden MCP server'a erişimi test et
docker-compose exec borsaci curl -I https://borsamcp.fastmcp.app/mcp
```

### Interactive Mode Çalışmıyor

**Çözüm**: `stdin_open: true` ve `tty: true` ayarlarının `docker-compose.yml`'de olduğundan emin olun.

```yaml
services:
    borsaci:
        stdin_open: true
        tty: true
```

### Container Hemen Kapanıyor

**Çözüm**: Logları kontrol edin:

```bash
docker-compose logs borsaci
```

## 🔒 Güvenlik

### API Key Güvenliği

-   `.env` dosyasını **asla** git'e commit etmeyin
-   `.gitignore` dosyasında `.env` olduğundan emin olun
-   Production'da Docker secrets kullanın:

```yaml
services:
    borsaci:
        secrets:
            - openrouter_api_key
        environment:
            - OPENROUTER_API_KEY_FILE=/run/secrets/openrouter_api_key

secrets:
    openrouter_api_key:
        file: ./secrets/openrouter_api_key.txt
```

### Network Güvenliği

-   Container'ı isolated network'te çalıştırın
-   Sadece gerekli portları expose edin
-   Firewall kurallarını yapılandırın

## 📊 Performans

### Image Boyutu Optimizasyonu

```bash
# Image boyutunu kontrol et
docker images borsaci

# Boyutu küçültmek için:
# 1. Multi-stage build kullanın
# 2. .dockerignore dosyasını optimize edin
# 3. Gereksiz dependencies'i kaldırın
```

### Memory Kullanımı

```bash
# Container memory kullanımını izle
docker stats borsaci

# Memory limit belirle
docker-compose run --rm -m 512m borsaci
```

## 🚢 Production Deployment

### Docker Hub'a Push

```bash
# Image'ı tag'le
docker tag borsaci:latest yourusername/borsaci:latest
docker tag borsaci:latest yourusername/borsaci:v0.2.0

# Docker Hub'a push et
docker push yourusername/borsaci:latest
docker push yourusername/borsaci:v0.2.0
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
    name: borsaci
spec:
    replicas: 1
    selector:
        matchLabels:
            app: borsaci
    template:
        metadata:
            labels:
                app: borsaci
        spec:
            containers:
                - name: borsaci
                  image: yourusername/borsaci:latest
                  env:
                      - name: OPENROUTER_API_KEY
                        valueFrom:
                            secretKeyRef:
                                name: borsaci-secrets
                                key: openrouter-api-key
                  stdin: true
                  tty: true
```

## 🔗 Faydalı Linkler

-   [Docker Documentation](https://docs.docker.com/)
-   [Docker Compose Documentation](https://docs.docker.com/compose/)
-   [BorsaCI GitHub](https://github.com/saidsurucu/borsaci)
-   [OpenRouter API](https://openrouter.ai/)

## 💡 İpuçları

1. **Development**: `docker-compose run --rm` kullanarak tek seferlik container'lar çalıştırın
2. **Production**: `docker-compose up -d` ile detached mode'da çalıştırın
3. **Debug**: `--debug` flag'i ile detaylı loglar alın
4. **Updates**: `docker-compose build --no-cache` ile temiz build yapın
5. **Cleanup**: Düzenli olarak `docker system prune` çalıştırın

## 🤝 Katkıda Bulunma

Docker yapılandırmasını geliştirmek için pull request gönderin!

---

**⭐ Eğer projeyi beğendiyseniz, GitHub'da yıldız vermeyi unutmayın!**
