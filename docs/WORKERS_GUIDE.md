# Workers Guide - Music Analysis Platform

Complete guide to the Celery workers and analysis pipeline.

## Overview

The platform uses Celery workers to perform asynchronous audio analysis. The pipeline consists of 5 phases, each handled by specialized workers:

```
YouTube URL
    ↓
[1] Extract Metadata (yt-dlp)
    ↓
[2] Fetch Text (YouTube captions or Whisper ASR)
    ↓
[3] Separate Sources (Demucs)
    ↓
[4] Analyze Audio (Essentia)
    ↓
[5] Postprocess Structure (LLM)
    ↓
Ready for Editing
```

## Architecture

### Worker Types

| Worker | Purpose | Technology | Duration |
|--------|---------|-----------|----------|
| **Audio Analysis** | BPM, key, features | Essentia | ~30-60s |
| **Source Separation** | Vocals, drums, bass, other | Demucs | ~2-5 min |
| **Speech Recognition** | Transcription & ASR | Whisper | ~30-90s |
| **Semantic Labeling** | Section labels, themes | LLM | ~15-30s |

### Task Queue

- **Message Broker**: Redis
- **Result Backend**: Redis or Postgres
- **Monitoring**: Flower (web UI)

## Phase Details

### Phase 1: Extract Metadata

**Task**: `extract_metadata_task`

Extracts video metadata from YouTube:
- Title
- Artist
- Duration
- Thumbnail
- Upload date

**Technology**: yt-dlp

**Duration**: ~5-10 seconds

**Error Handling**:
- Invalid URL → Immediate failure
- Video not found → Immediate failure
- Private/restricted video → Immediate failure

**Output**:
```json
{
  "title": "Amazing Grace",
  "artist": "John Newton",
  "duration": 240,
  "thumbnail_url": "https://...",
  "upload_date": "2023-01-15"
}
```

### Phase 2: Fetch Text

**Task**: `fetch_text_task`

Fetches lyrics/captions from video:
1. Try YouTube captions (auto-generated or manual)
2. Fallback to Whisper ASR if no captions

**Technology**: YouTube API + Whisper

**Duration**: ~30-90 seconds (depending on fallback)

**Confidence Scoring**:
- Manual captions: 0.95-0.99
- Auto-generated captions: 0.85-0.95
- Whisper ASR: 0.80-0.95

**Output**:
```json
{
  "text": "Amazing grace, how sweet the sound...",
  "source": "captions",
  "language": "en",
  "confidence": 0.92,
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "Amazing grace, how sweet the sound"
    }
  ]
}
```

### Phase 3: Separate Sources

**Task**: `separate_sources_task`

Separates audio into stems using Demucs:
- Vocals
- Drums
- Bass
- Other instruments

**Technology**: Demucs (Facebook Research)

**Duration**: ~2-5 minutes (GPU: ~30-60s, CPU: ~5-10 min)

**Optional**: Can be skipped if not needed

**Output**:
```json
{
  "stems": {
    "vocals": "s3://bucket/analysis_id/vocals.wav",
    "drums": "s3://bucket/analysis_id/drums.wav",
    "bass": "s3://bucket/analysis_id/bass.wav",
    "other": "s3://bucket/analysis_id/other.wav"
  },
  "stem_prominence": {
    "vocals": 0.35,
    "drums": 0.25,
    "bass": 0.20,
    "other": 0.20
  }
}
```

### Phase 4: Analyze Audio

**Task**: `analyze_audio_task`

Analyzes audio features using Essentia:
- BPM detection
- Key/tonality detection
- Feature extraction (MFCC, spectral, temporal)
- Section detection
- Chord detection

**Technology**: Essentia (Music Technology Group)

**Duration**: ~30-60 seconds

**Output**:
```json
{
  "bpm": 120.0,
  "bpm_confidence": 0.92,
  "key": "G major",
  "key_confidence": 0.87,
  "sections": [
    {
      "type": "intro",
      "start": 0.0,
      "end": 10.0,
      "confidence": 0.95
    }
  ],
  "chords": [
    {
      "time": 0.0,
      "chord": "G",
      "confidence": 0.95
    }
  ],
  "features": {
    "mfcc_mean": [...],
    "spectral_centroid": 2500.0,
    "zero_crossing_rate": 0.15
  }
}
```

### Phase 5: Postprocess Structure

**Task**: `postprocess_structure_task`

Uses LLM to add semantic analysis:
- Section labeling (verse, chorus, bridge, etc.)
- Emotional tone detection
- Lyrical theme extraction
- Arrangement suggestions
- Worship context analysis

**Technology**: OpenAI GPT, Claude, or similar

**Duration**: ~15-30 seconds

**Output**:
```json
{
  "section_labels": [
    {
      "section_id": "sec_0",
      "role": "introduction",
      "emotional_tone": "peaceful",
      "description": "Soft introduction...",
      "confidence": 0.92
    }
  ],
  "lyrical_themes": [
    {
      "theme": "Grace and Redemption",
      "keywords": ["grace", "saved", "wretch"],
      "sentiment": "positive",
      "confidence": 0.96
    }
  ],
  "overall_mood": "Uplifting and contemplative",
  "suggested_arrangement_notes": [
    "Start with soft piano...",
    "Build gradually through verses..."
  ]
}
```

## Running Workers

### Start Audio Analysis Worker

```bash
cd apps/worker-audio
celery -A celery_pipeline worker --loglevel=info --concurrency=2
```

### Start Semantic Worker

```bash
cd apps/worker-semantic
celery -A llm_labeler worker --loglevel=info --concurrency=1
```

### Monitor with Flower

```bash
celery -A celery_pipeline flower
# Visit http://localhost:5555
```

### Run Beat Scheduler

```bash
celery -A celery_pipeline beat --loglevel=info
```

## Configuration

### Environment Variables

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=postgresql://user:pass@localhost/music_analysis

# Audio Processing
ESSENTIA_CACHE_DIR=/tmp/essentia_cache
DEMUCS_MODEL=htdemucs
DEMUCS_DEVICE=cuda  # or cpu

# Speech Recognition
WHISPER_MODEL=base
WHISPER_DEVICE=cuda

# LLM
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7

# Storage
S3_BUCKET=music-analysis-bucket
S3_REGION=us-east-1
```

### Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker-audio:
    build: ./apps/worker-audio
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://...
    depends_on:
      - redis

  worker-semantic:
    build: ./apps/worker-semantic
    environment:
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=...
    depends_on:
      - redis

  flower:
    image: mher/flower
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
```

## Error Handling

### Retry Strategy

| Phase | Max Retries | Backoff | Timeout |
|-------|------------|---------|---------|
| Extract Metadata | 3 | exponential | 30s |
| Fetch Text | 2 | exponential | 120s |
| Separate Sources | 1 | fixed | 600s |
| Analyze Audio | 2 | exponential | 120s |
| Postprocess | 2 | exponential | 60s |

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `InvalidURLError` | Bad YouTube URL | Validate URL format |
| `VideoNotFoundError` | Video deleted/private | Inform user |
| `AudioExtractionError` | Failed to extract audio | Retry or skip |
| `OutOfMemoryError` | Large file on CPU | Use GPU or reduce quality |
| `TimeoutError` | Processing took too long | Increase timeout or use GPU |
| `LLMError` | API rate limit or error | Retry with backoff |

### Error Notification

Failed analyses trigger:
1. Database status update (phase: "failed", error_message: "...")
2. Audit log entry
3. Optional: Email notification to organization admin
4. Optional: Slack notification

## Monitoring

### Metrics to Track

- **Queue Depth**: Number of pending tasks
- **Worker Health**: CPU, memory, uptime
- **Task Duration**: Per-phase timing
- **Success Rate**: % of successful analyses
- **Error Rate**: % of failed analyses
- **Confidence Scores**: Average confidence per phase

### Prometheus Metrics

```
music_analysis_queue_depth
music_analysis_task_duration_seconds
music_analysis_task_success_total
music_analysis_task_error_total
music_analysis_confidence_score
```

### Logging

All workers log to:
- Console (development)
- Syslog (production)
- CloudWatch (AWS)
- ELK Stack (enterprise)

Log levels:
- `DEBUG`: Detailed task execution
- `INFO`: Phase transitions
- `WARNING`: Degraded performance
- `ERROR`: Task failures
- `CRITICAL`: Worker crashes

## Performance Optimization

### GPU Acceleration

For faster processing, use GPU:

```bash
# Demucs with GPU
DEMUCS_DEVICE=cuda celery worker

# Whisper with GPU
WHISPER_DEVICE=cuda celery worker
```

**GPU Requirements**:
- Demucs: ~4GB VRAM
- Whisper: ~2GB VRAM
- Essentia: CPU only

### Caching

Results are cached in Redis:
- BPM detection: 24 hours
- Key detection: 24 hours
- Transcriptions: 7 days
- Semantic analysis: 30 days

### Batch Processing

For bulk imports, use batch mode:

```python
from celery import group

# Process 100 songs in parallel
job = group([
    analyze_song_task.s(song_id)
    for song_id in song_ids
])
result = job.apply_async()
```

## Testing

### Unit Tests

```bash
pytest apps/worker-audio/tests/ -v
```

### Integration Tests

```bash
pytest tests/integration/test_workers.py -v
```

### Load Testing

```bash
locust -f tests/load/locustfile.py
```

## Troubleshooting

### Worker Not Processing Tasks

```bash
# Check Redis connection
redis-cli ping

# Check Celery status
celery -A celery_pipeline inspect active

# Check worker logs
celery -A celery_pipeline worker --loglevel=debug
```

### High Memory Usage

```bash
# Reduce concurrency
celery worker --concurrency=1

# Enable memory limits
celery worker --max-memory-per-child=200000
```

### Slow Processing

```bash
# Use GPU
DEMUCS_DEVICE=cuda celery worker

# Increase concurrency
celery worker --concurrency=4

# Check system resources
htop
```

## Production Deployment

### Systemd Service

```ini
[Unit]
Description=Music Analysis Worker
After=network.target

[Service]
Type=forking
User=celery
WorkingDirectory=/app
ExecStart=/usr/bin/celery -A celery_pipeline worker
Restart=always

[Install]
WantedBy=multi-user.target
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: music-analysis-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: music-analysis-worker
  template:
    metadata:
      labels:
        app: music-analysis-worker
    spec:
      containers:
      - name: worker
        image: music-analysis-worker:latest
        env:
        - name: REDIS_URL
          value: redis://redis:6379/0
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Essentia Documentation](https://essentia.upf.edu/)
- [Demucs GitHub](https://github.com/facebookresearch/demucs)
- [Whisper GitHub](https://github.com/openai/whisper)
- [OpenAI API](https://platform.openai.com/docs/)
