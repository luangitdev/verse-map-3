# 🐳 Docker Troubleshooting Guide - Verse Map

Este guia ajuda a resolver problemas comuns ao fazer build e rodar o Verse Map com Docker.

## 🔴 Erro: `apt-get update` falha com exit code 100

### Sintomas
```
failed to solve: process "/bin/sh -c apt-get update..." did not complete successfully: exit code: 100
```

### Causas Possíveis
1. **Imagem base instável** - Alpine Linux pode ter repositórios instáveis
2. **Problemas de rede** - Conexão lenta ou intermitente
3. **Mirror de pacotes indisponível** - Repositório Debian offline
4. **Cache corrompido** - Build cache antigo

### Soluções

#### Solução 1: Limpar cache Docker (RECOMENDADO)
```bash
# Parar containers
docker-compose down

# Remover imagens
docker-compose rm -f

# Limpar cache de build
docker builder prune -a

# Tentar novamente
docker-compose up -d --build
```

#### Solução 2: Usar BuildKit (mais robusto)
```bash
# Habilitar BuildKit
export DOCKER_BUILDKIT=1

# Fazer build
docker-compose build --no-cache
```

#### Solução 3: Aumentar timeout
```bash
# Editar docker-compose.yml e adicionar:
build:
  context: ./apps/worker-audio
  dockerfile: Dockerfile
  args:
    BUILDKIT_INLINE_CACHE: 1
```

#### Solução 4: Usar imagem base mais estável
```dockerfile
# Usar Debian Bullseye em vez de Alpine
FROM python:3.11-bullseye
```

---

## 🔴 Erro: "No space left on device"

### Sintomas
```
failed to solve: failed to write to output stream: no space left on device
```

### Causas
- Disco cheio com imagens Docker antigas
- Volumes Docker grandes
- Build cache ocupando muito espaço

### Soluções

```bash
# Ver uso de disco
docker system df

# Limpar tudo (CUIDADO!)
docker system prune -a

# Remover volumes não usados
docker volume prune

# Remover imagens não usadas
docker image prune -a

# Remover containers parados
docker container prune
```

---

## 🔴 Erro: "Cannot connect to Docker daemon"

### Sintomas
```
Cannot connect to Docker daemon at unix:///var/run/docker.sock
```

### Soluções

#### macOS/Windows
- Abra **Docker Desktop**
- Aguarde inicialização completa

#### Linux
```bash
# Inicie o Docker
sudo systemctl start docker

# Ou
sudo service docker start

# Adicione seu usuário ao grupo docker (opcional)
sudo usermod -aG docker $USER
newgrp docker
```

---

## 🔴 Erro: "Port already in use"

### Sintomas
```
Error response from daemon: driver failed programming external connectivity on endpoint
```

### Soluções

```bash
# Encontre o processo usando a porta
lsof -i :3000   # Frontend
lsof -i :8000   # API
lsof -i :5432   # Postgres
lsof -i :6379   # Redis
lsof -i :5555   # Flower

# Mate o processo
kill -9 <PID>

# Ou use outra porta no docker-compose.yml
ports:
  - "3001:3000"  # Usar 3001 em vez de 3000
```

---

## 🔴 Erro: "pip install" falha com "Could not find a version"

### Sintomas
```
ERROR: Could not find a version that satisfies the requirement essentia==2.1.0
```

### Causas
- Pacote não disponível para Python 3.11
- Versão descontinuada
- PyPI offline

### Soluções

```bash
# Atualizar pip
pip install --upgrade pip

# Tentar versão mais nova
# Editar requirements.txt com versão compatível

# Ou instalar do source
pip install git+https://github.com/essentia/essentia.git

# Usar mirror PyPI alternativo
pip install -i https://mirrors.aliyun.com/pypi/simple/ essentia
```

---

## 🔴 Erro: "Build takes too long" ou "timeout"

### Sintomas
- Build fica preso por mais de 30 minutos
- Timeout durante `pip install`

### Causas
- Compilação de pacotes pesados (Torch, Essentia)
- Conexão de internet lenta
- Recursos limitados

### Soluções

#### Aumentar timeout
```bash
# No docker-compose.yml
build:
  context: ./apps/worker-audio
  dockerfile: Dockerfile
  args:
    BUILDKIT_INLINE_CACHE: 1
```

#### Usar imagens pré-compiladas
```dockerfile
# Em vez de compilar Torch
FROM pytorch/pytorch:2.1.0-runtime-cuda12.1-runtime

# Depois instalar outras dependências
RUN pip install essentia librosa
```

#### Aumentar recursos Docker
- **Docker Desktop → Preferences → Resources**
- CPU: 4+ cores
- Memory: 8GB+
- Disk: 20GB+

---

## 🔴 Erro: "Worker não conecta ao Redis"

### Sintomas
```
Error: Cannot connect to redis://redis:6379/0
```

### Soluções

```bash
# Verificar se Redis está rodando
docker-compose ps redis

# Ver logs do Redis
docker-compose logs redis

# Testar conexão
docker-compose exec redis redis-cli ping

# Reiniciar Redis
docker-compose restart redis
```

---

## 🔴 Erro: "Worker não conecta ao Postgres"

### Sintomas
```
Error: Cannot connect to postgresql://...@postgres:5432/...
```

### Soluções

```bash
# Verificar se Postgres está rodando
docker-compose ps postgres

# Ver logs do Postgres
docker-compose logs postgres

# Testar conexão
docker-compose exec postgres psql -U music_user -d music_analysis -c "SELECT 1"

# Reiniciar Postgres
docker-compose restart postgres
```

---

## 🔴 Erro: "Frontend não conecta à API"

### Sintomas
```
Error: Cannot GET /api/health
CORS error
```

### Soluções

```bash
# Verificar se API está rodando
docker-compose ps api

# Ver logs da API
docker-compose logs api

# Testar conexão
curl http://localhost:8000/docs

# Verificar variável de ambiente
docker-compose exec web env | grep API_URL
```

---

## ✅ Verificação de Saúde

### Checklist de Inicialização

```bash
# 1. Verificar containers
docker-compose ps

# 2. Verificar logs
docker-compose logs -f

# 3. Testar conexões
# Postgres
docker-compose exec postgres psql -U music_user -d music_analysis -c "SELECT 1"

# Redis
docker-compose exec redis redis-cli ping

# API
curl http://localhost:8000/docs

# Frontend
curl http://localhost:3000

# 4. Verificar workers
docker-compose logs worker-audio | tail -20
docker-compose logs worker-semantic | tail -20

# 5. Acessar Flower
open http://localhost:5555
```

---

## 🚀 Performance Tips

### Acelerar Build

```bash
# 1. Usar BuildKit
export DOCKER_BUILDKIT=1

# 2. Usar cache
docker-compose build --cache-from

# 3. Parallelizar
docker-compose build --parallel

# 4. Usar imagens pré-compiladas
# Editar Dockerfile para usar pytorch/pytorch:2.1.0-runtime-cuda12.1-runtime
```

### Acelerar Execução

```bash
# 1. Aumentar recursos
# Docker Desktop → Preferences → Resources
# CPU: 4+ cores
# Memory: 8GB+

# 2. Usar volumes nomeados
docker volume create postgres_data
docker volume create redis_data

# 3. Desabilitar hot reload em produção
# docker-compose.yml: command: npm run build && npm start
```

---

## 📊 Monitoramento

### Ver Uso de Recursos

```bash
# CPU, Memory, Network
docker stats

# Disco
docker system df

# Imagens
docker images

# Containers
docker ps -a

# Volumes
docker volume ls
```

---

## 🔧 Comandos Úteis

```bash
# Logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f api

# Últimas 100 linhas
docker-compose logs --tail 100 api

# Executar comando em container
docker-compose exec api python -m pytest

# Shell em container
docker-compose exec api bash

# Rebuild sem cache
docker-compose build --no-cache

# Parar tudo
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Remover tudo
docker system prune -a --volumes
```

---

## 📞 Quando Pedir Ajuda

Se o problema persistir, forneça:

1. **Output completo do erro**
   ```bash
   docker-compose up -d 2>&1 | tee error.log
   ```

2. **Versão do Docker**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Recursos disponíveis**
   ```bash
   docker system df
   docker stats --no-stream
   ```

4. **Logs dos containers**
   ```bash
   docker-compose logs > logs.txt
   ```

5. **Seu sistema operacional**
   - macOS (versão)
   - Windows (versão, WSL2 ou Hyper-V)
   - Linux (distribuição)

---

## 🎯 Próximas Ações

1. Limpe o cache: `docker system prune -a`
2. Tente novamente: `docker-compose up -d --build`
3. Verifique saúde: `docker-compose ps`
4. Acesse: http://localhost:3000

Boa sorte! 🚀
