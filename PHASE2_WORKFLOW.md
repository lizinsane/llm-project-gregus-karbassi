# Phase 2: Visual Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: PDF PROCESSING                       │
│                         (Test First!)                            │
└─────────────────────────────────────────────────────────────────┘

                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Place PDF in         │
                    │  data/raw/            │
                    └───────────────────────┘
                                │
                                ▼
        ╔═══════════════════════════════════════════╗
        ║         STEP 1: TEST MODE (10 pages)      ║
        ╚═══════════════════════════════════════════╝
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌────────────────────┐  ┌────────────────────┐
        │  pdf_processor.py  │  │  Try Docling first │
        │      --test        │  │  Fallback: PyPDF   │
        └────────────────────┘  └────────────────────┘
                    │
                    ├─► Extracts pages 1-10
                    ├─► Cleans text
                    └─► Saves to test_extracted_text.json
                                │
                                ▼
                    ┌───────────────────────┐
                    │     chunker.py        │
                    │       --test          │
                    └───────────────────────┘
                                │
                    ├─► Splits into chunks
                    ├─► Adds metadata (page #)
                    └─► Saves to test_chunks.json
                                │
                                ▼
                    ┌───────────────────────┐
                    │  chunk_analyzer.py    │
                    │       --test          │
                    └───────────────────────┘
                                │
                    ├─► Shows statistics
                    ├─► Displays samples
                    └─► Gives recommendations
                                │
                                ▼
                        ┌───────────────┐
                        │  Review       │
                        │  Chunks OK?   │
                        └───────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                   NO                      YES
                    │                       │
                    ▼                       ▼
        ┌────────────────────┐  ┌────────────────────┐
        │  Adjust config:    │  │  Proceed to        │
        │  - chunk_size      │  │  FULL processing   │
        │  - chunk_overlap   │  │                    │
        └────────┬───────────┘  └────────────────────┘
                 │                         │
                 └─────► Re-run ──────────┘
                         chunker
                                │
                                ▼
        ╔═══════════════════════════════════════════╗
        ║      STEP 2: FULL MODE (274 pages)        ║
        ╚═══════════════════════════════════════════╝
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌────────────────────┐  ┌────────────────────┐
        │  pdf_processor.py  │  │  Process all 274   │
        │      --full        │  │  pages (5-15 min)  │
        └────────────────────┘  └────────────────────┘
                    │
                    └─► Saves to extracted_text.json
                                │
                                ▼
                    ┌───────────────────────┐
                    │     chunker.py        │
                    │       --full          │
                    └───────────────────────┘
                                │
                    └─► Saves to chunks.json
                                │
                                ▼
                    ┌───────────────────────┐
                    │  ~1,200-1,500 chunks  │
                    │  Ready for Phase 3!   │
                    └───────────────────────┘
                                │
                                ▼
                              DONE
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Ready for Phase 3:  │
                    │    RAG Pipeline!      │
                    └───────────────────────┘
```

## File Flow

```
data/raw/
  └── Illustrierte_Schweizer_Geschichte.pdf (INPUT)
        │
        ├─── [pdf_processor --test] ───►
        │
data/processed/
  ├── test_extracted_text.json (10 pages)
        │
        ├─── [chunker --test] ───►
        │
  ├── test_chunks.json (test chunks)
        │
        ├─── [chunk_analyzer --test] ───►
        │
  └── [Review & Adjust] ───► If OK, continue ───►
        │
        ├─── [pdf_processor --full] ───►
        │
  ├── extracted_text.json (274 pages)
        │
        ├─── [chunker --full] ───►
        │
  └── chunks.json (final chunks) ───► READY FOR PHASE 3!
```

## Key Scripts

```
src/ingestion/
├── pdf_processor.py       → Extracts text from PDF
│   ├── --test            → First 10 pages
│   └── --full            → All 274 pages
│
├── chunker.py             → Splits text into chunks
│   ├── --test            → Process test data
│   └── --full            → Process full data
│
└── chunk_analyzer.py      → Analyzes chunk quality
    ├── --test            → Analyze test chunks
    └── --full            → Analyze full chunks
```

## Configuration

```
config/config.yaml
    └── pdf_processing:
        ├── chunk_size: 1000        ← Adjust if needed
        ├── chunk_overlap: 200      ← Adjust if needed
        └── min_chunk_size: 100
```

## Decision Points

```
1. Docling vs PyPDF?
   → Try Docling first (better quality)
   → Use PyPDF if Docling fails (--no-docling flag)

2. Chunks look good?
   → YES: Proceed to full processing
   → NO: Adjust config and re-run test

3. What chunk_size to use?
   → 800-1000: Good for detailed answers
   → 1000-1500: Good for broader context
   → Adjust based on your analysis
```

## Time Breakdown

```
│
├─ Setup PDF (1 min)
│
├─ Test Processing (5 min)
│   ├─ Extract 10 pages (2-3 min)
│   ├─ Chunk (1 min)
│   └─ Analyze (1 min)
│
├─ Adjust if needed (5-15 min)
│
└─ Full Processing (15 min)
    ├─ Extract 274 pages (5-15 min)
    └─ Chunk (1-2 min)
    
TOTAL: 15-40 minutes
```

## Success Indicators

```
✅ Text extraction:
   • Readable German text
   • No encoding issues
   • Page numbers tracked

✅ Chunking:
   • Average size: 800-1200 chars
   • Consistent sizes
   • Complete thoughts
   • Good overlap

✅ Ready for Phase 3:
   • chunks.json created
   • ~1,200+ chunks
   • Quality verified
```
