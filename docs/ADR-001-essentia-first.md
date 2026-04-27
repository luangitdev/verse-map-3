# ADR-001: Essentia as Primary Music Information Retrieval Engine

## Status
Accepted

## Context

The platform requires robust Music Information Retrieval (MIR) capabilities to automatically detect BPM, tonality, and structural features from audio. Multiple MIR libraries exist:

- **Essentia**: Comprehensive, industry-standard, supports real-time analysis, active development
- **Librosa**: Python-first, good for research, lighter weight
- **Sonic Annotator**: Vamp plugin framework, modular but complex
- **Chroma**: Specialized for chord recognition, limited scope

The choice of MIR engine directly impacts:
1. Analysis accuracy and confidence scores
2. Feature richness (BPM, key, onsets, chroma, MFCC, etc.)
3. Computational cost and latency
4. Extensibility for future features

## Decision

**Use Essentia as the primary MIR engine for the audio analysis worker.**

## Rationale

1. **Comprehensive Feature Set**: Essentia provides BPM detection, key detection, onset detection, chroma features, MFCC, and spectral features in a single library, reducing complexity.

2. **Industry Standard**: Widely used in music streaming (Spotify uses Essentia for recommendations), research, and production systems.

3. **Confidence Scores**: Essentia returns confidence metrics for key results, enabling the UI to signal uncertain detections.

4. **Real-time Capable**: Supports streaming analysis, useful for future live-mode enhancements.

5. **Active Development**: Maintained by MTG (Music Technology Group), with regular updates and community support.

6. **Python Integration**: Clean Python bindings via `essentia-extractor` or direct library, fitting the Celery worker architecture.

7. **Extensibility**: Can be combined with other libraries (Librosa for additional features, Demucs for source separation) without conflicts.

## Consequences

### Positive
- Single source of truth for audio features
- Consistent confidence scoring across BPM, key, and structure
- Reduced worker complexity and maintenance burden
- Easy to add new audio features (onsets, tempogram, etc.)

### Negative
- Essentia has a learning curve for parameter tuning
- Some edge cases (unusual time signatures, live recordings) may require post-processing
- Computational cost is moderate (5-30 seconds per 3-minute song depending on quality)

## Alternatives Considered

### Librosa + Custom Logic
Would require building confidence scoring and feature extraction from scratch. More flexible but higher maintenance.

### Sonic Annotator + Vamp Plugins
Modular but adds operational complexity (plugin management, version control).

### Chroma-Only
Too specialized; would miss BPM and key detection.

## Implementation Notes

1. **Worker Setup**: Install `essentia` in the audio worker container
2. **Feature Extraction**: Compute BPM, key, onsets, chroma in a single pass to minimize I/O
3. **Confidence Thresholds**: Define minimum confidence for BPM (0.7), key (0.6), structure (0.5)
4. **Caching**: Cache Essentia results by audio hash to avoid recomputation
5. **Fallback**: If Essentia fails, mark analysis as `partial` and allow manual input

## Related Decisions

- ADR-002: Multi-tenant RLS strategy
- ADR-003: Async pipeline with Celery (TBD)

## References

- Essentia Documentation: https://essentia.upf.edu/
- MTG Research: https://www.upf.edu/web/mtg
