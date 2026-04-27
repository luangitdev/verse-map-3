# 🚀 Guia de Desenvolvimento Local - Verse Map

Este guia fornece instruções completas para rodar a plataforma Verse Map localmente em sua máquina.

## 📋 Pré-requisitos

### Opção 1: Com Docker (Recomendado)
- **Docker Desktop** (Windows, Mac) ou **Docker + Docker Compose** (Linux)
- **Git**
- **Mínimo 8GB RAM** (16GB recomendado)
- **10GB espaço em disco** (para imagens Docker)

### Opção 2: Sem Docker (Desenvolvimento Nativo)
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 16**
- **Redis 7**
- **FFmpeg**
- **Git**
- **Mínimo 16GB RAM** (para compilação de dependências)
- **20GB espaço em disco**

---

## 🐳 Opção 1: Com Docker Compose (Mais Fácil)

### 1.1 Clonar o Repositório

```bash
git clone https://github.com/luangitdev/verse-map-3.git
cd verse-map-3
```

### 1.2 Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas configurações:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/verse_map
POSTGRES_PASSWORD=postgres

# Redis
REDIS_URL=redis://redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# JWT
JWT_SECRET=your-secret-key-change-this

# OpenAI (para LLM)
OPENAI_API_KEY=sk-your-key-here
```

### 1.3 Iniciar Stack Completo

```bash
docker-compose up -d
```

**Primeira execução**: Pode levar **15-30 minutos** (compilação de dependências)

### 1.4 Verificar Status

```bash
docker-compose ps
```

Você deve ver:

```
NAME                    STATUS
postgres                Up (healthy)
redis                   Up (healthy)
api                     Up
worker-audio            Up
worker-semantic         Up
web                     Up
flower                  Up
pgadmin                 Up
```

### 1.5 Acessar Aplicação

| Serviço | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Flower** (Celery) | http://localhost:5555 |
| **pgAdmin** | http://localhost:5050 |

### 1.6 Parar Stack

```bash
docker-compose down
```

### 1.7 Remover Tudo (incluindo volumes)

```bash
docker-compose down -v
```

---

## 💻 Opção 2: Desenvolvimento Nativo (Sem Docker)

### 2.1 Clonar o Repositório

```bash
git clone https://github.com/luangitdev/verse-map-3.git
cd verse-map-3
```

### 2.2 Instalar PostgreSQL

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Windows
[Download PostgreSQL](https://www.postgresql.org/download/windows/)

### 2.3 Instalar Redis

#### macOS
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

#### Windows
[Download Redis](https://github.com/microsoftarchive/redis/releases)

### 2.4 Instalar FFmpeg

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt-get install ffmpeg
```

#### Windows
[Download FFmpeg](https://ffmpeg.org/download.html)

### 2.5 Criar Banco de Dados

```bash
createdb verse_map
```

### 2.6 Configurar Backend

```bash
cd apps/api

# Criar virtual environment
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp ../../.env.example .env

# Rodar migrations (se houver)
# alembic upgrade head
```

### 2.7 Iniciar Backend

```bash
# Terminal 1: API
cd apps/api
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2.8 Iniciar Workers Celery

```bash
# Terminal 2: Audio Worker
cd apps/worker-audio
source venv/bin/activate
celery -A celery_pipeline worker --loglevel=info

# Terminal 3: Semantic Worker
cd apps/worker-semantic
source venv/bin/activate
celery -A llm_labeler worker --loglevel=info

# Terminal 4: Celery Beat (Scheduler)
cd apps/worker-audio
source venv/bin/activate
celery -A celery_pipeline beat --loglevel=info

# Terminal 5: Flower (Monitoring)
cd apps/worker-audio
source venv/bin/activate
celery -A celery_pipeline flower
```

### 2.9 Iniciar Frontend

```bash
# Terminal 6: Frontend
cd apps/web
npm install
npm run dev
```

### 2.10 Acessar Aplicação

| Serviço | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Flower** | http://localhost:5555 |

---

## 🔧 Troubleshooting

### Docker Issues

#### Erro: "Cannot connect to Docker daemon"
```bash
# macOS/Windows: Inicie o Docker Desktop

# Linux: Inicie o Docker
sudo systemctl start docker
```

#### Erro: "Port already in use"
```bash
# Encontre o processo usando a porta
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # Postgres
lsof -i :6379  # Redis

# Mate o processo
kill -9 <PID>
```

#### Build muito lento
- Verifique sua conexão de internet
- Aumente o timeout: `docker-compose up --build --timeout 300`
- Limpe cache: `docker system prune -a`

### Backend Issues

#### Erro: "ModuleNotFoundError"
```bash
# Reinstale dependências
pip install --upgrade -r requirements.txt
```

#### Erro: "psycopg2: cannot import name 'compat'"
```bash
# Reinstale psycopg2
pip uninstall psycopg2-binary
pip install psycopg2-binary==2.9.9
```

#### Erro: "Connection refused" (Postgres)
```bash
# Verifique se Postgres está rodando
psql -U postgres -d verse_map

# Se não estiver, inicie
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS
```

### Frontend Issues

#### Erro: "Cannot find module"
```bash
# Limpe node_modules e reinstale
rm -rf node_modules package-lock.json
npm install
```

#### Porta 3000 já em uso
```bash
# Use outra porta
npm run dev -- -p 3001
```

### Worker Issues

#### Celery não conecta ao Redis
```bash
# Verifique se Redis está rodando
redis-cli ping  # Deve retornar "PONG"

# Se não estiver, inicie
sudo systemctl start redis-server  # Linux
brew services start redis  # macOS
```

#### Erro: "No module named 'essentia'"
```bash
# Essentia é opcional, instale se necessário
pip install essentia

# Ou comente a linha em requirements.txt se não precisar
```

---

## 📊 Monitoramento

### Logs

#### Docker
```bash
# Ver logs de um serviço
docker-compose logs api
docker-compose logs worker-audio
docker-compose logs web

# Seguir logs em tempo real
docker-compose logs -f api

# Ver últimas 100 linhas
docker-compose logs --tail 100 api
```

#### Nativo
```bash
# Logs estão no terminal onde o serviço foi iniciado
# Use Ctrl+C para parar
```

### Flower (Celery Monitoring)

Acesse: http://localhost:5555

Você verá:
- Tasks em execução
- Tasks completadas
- Erros de tasks
- Performance metrics

### pgAdmin (Database Management)

Acesse: http://localhost:5050

**Login**:
- Email: `admin@admin.com`
- Senha: `admin`

**Conectar ao Postgres**:
1. Clique em "Add New Server"
2. Nome: `verse_map`
3. Host: `postgres`
4. Username: `postgres`
5. Password: `postgres`

---

## 🧪 Testes

### Rodar Testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas unit tests
pytest tests/unit/ -v

# Apenas integration tests
pytest tests/integration/ -v

# Apenas E2E tests
pytest tests/e2e/ -v

# Com coverage
pytest tests/ --cov=apps --cov-report=html
```

### BDD Tests

```bash
# Instale behave
pip install behave

# Rode testes BDD
behave tests/bdd/
```

---

## 🚀 Performance Tips

### Docker

1. **Use BuildKit** (mais rápido):
   ```bash
   DOCKER_BUILDKIT=1 docker-compose build
   ```

2. **Aumente recursos**:
   - Docker Desktop → Preferences → Resources
   - CPU: 4+ cores
   - Memory: 8GB+
   - Disk: 20GB+

3. **Use volumes nomeados**:
   ```bash
   docker volume create postgres_data
   docker volume create redis_data
   ```

### Desenvolvimento Nativo

1. **Use Python venv** (não global)
2. **Use npm ci** em vez de npm install
3. **Ative hot reload**:
   ```bash
   npm run dev  # Frontend
   python -m uvicorn main:app --reload  # Backend
   ```

---

## 📝 Estrutura de Pastas

```
verse-map-3/
├── apps/
│   ├── api/              ← Backend FastAPI
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routers/
│   │   └── requirements.txt
│   ├── web/              ← Frontend Next.js
│   │   ├── src/
│   │   ├── package.json
│   │   └── next.config.js
│   ├── worker-audio/     ← Audio Worker
│   │   ├── celery_pipeline.py
│   │   └── requirements.txt
│   └── worker-semantic/  ← LLM Worker
│       ├── llm_labeler.py
│       └── requirements.txt
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── bdd/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔐 Segurança

### Desenvolvimento Local

1. **Mude JWT_SECRET**:
   ```env
   JWT_SECRET=seu-secret-aleatorio-aqui
   ```

2. **Mude senhas padrão**:
   ```env
   POSTGRES_PASSWORD=sua-senha-forte
   PGADMIN_DEFAULT_PASSWORD=sua-senha-forte
   ```

3. **Não commit .env**:
   ```bash
   # Já está em .gitignore
   ```

### Produção

- Use variáveis de ambiente seguras
- Ative SSL/TLS
- Configure CORS corretamente
- Use secrets manager (AWS Secrets, HashiCorp Vault)
- Ative rate limiting
- Configure backup automático

---

## 📚 Documentação Adicional

- [README.md](README.md) - Visão geral do projeto
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Documentação de endpoints
- [WORKERS_GUIDE.md](docs/WORKERS_GUIDE.md) - Guia de workers
- [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) - Guia de testes
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Deploy em produção

---

## 💡 Dicas Úteis

### Limpar Cache Docker
```bash
docker system prune -a
docker volume prune
```

### Rebuild sem cache
```bash
docker-compose build --no-cache
```

### Executar comando em container
```bash
docker-compose exec api python -m pytest
docker-compose exec web npm run build
```

### Acessar shell do container
```bash
docker-compose exec api bash
docker-compose exec web sh
```

### Ver variáveis de ambiente
```bash
docker-compose exec api env | grep DATABASE
```

---

## 🎯 Próximas Ações

1. ✅ Clone o repositório
2. ✅ Configure `.env`
3. ✅ Escolha: Docker ou Nativo
4. ✅ Siga as instruções
5. ✅ Acesse http://localhost:3000
6. ✅ Comece a desenvolver!

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique a seção **Troubleshooting**
2. Consulte os logs
3. Abra uma issue no GitHub
4. Verifique a documentação

---

**Boa sorte! 🚀**
