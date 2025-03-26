# AI GRADER-LYSA


## Directory Structure

```
AI_GRADER-LYSA/
│
├── app/                         # Flask application
│   ├── __init__.py              # Package initializer
│   ├── app.py                   # Main application entry point
│   ├── config.py                # Application configuration
│   ├── routes.py                # Web routes definitions
│   ├── utils.py                 # Utility functions
│   └── templates/               # HTML templates (not shown)
│
├── services/                    # Core services of the application
│   ├── evaluator/               # Evaluation logic
│   │   ├── evaluator.py         # Main evaluation module
│   │   └── llm_exp.py           # LLM-based evaluation
│   │
│   ├── input/                   # Input handling
│   │   └── capture.py           # File upload capture
│   │
│   ├── nlp/                     # Natural Language Processing
│   │   ├── similarity.py        # Text similarity metrics
│   │   └── tokenizer.py         # Text tokenization
│   │
│   └── ocr/                     # Optical Character Recognition
│       ├── ocr_engine.py        # Main OCR processor
│       ├── preprocess.py        # Image preprocessing
│       └── ocr_postprocess/     # OCR result processing
│           ├── formula_detector.py  # Mathematical formula detection
│           └── merger.py            # Text merging utilities
│
├── uploads/                     # Storage for uploaded files
│   └── GROUPS/                  # Organized by class/group
│       └── CLASS-G1/            # Example class
│           ├── Students/        # Individual student submissions
│           │   └── 1/           # Student ID
│           │       └── subjects/
│           │           └── english/
│           │               └── test_id/
│           │                   ├── evaluation_results/
│           │                   │   └── result.txt
│           │                   └── README.md
│           │
│           ├── Subjects/        # Subject-specific files
│           │   └── English/     # Example subject
│           │       └── test1/   # Test identifier
│           │           └── results.csv
│           │
│           └── records          # Class records
│
├── main.py                      # Application entry point
└── requirements.txt             # Python dependencies
```

## Workflow

### 1. File Submission
- Students or teachers upload answer scripts (images/PDFs) via the web interface

### 2. Text Extraction
- The OCR engine processes the uploaded files:
  1. Images are preprocessed to improve quality (deskewing, enhancing contrast)
  2. Pytesseract extracts text from the preprocessed images
  3. Special handling for mathematical formulas is applied when detected

### 3. Text Analysis
- The extracted text undergoes NLP processing by tokenization

### 4. Evaluation
- The system evaluates the processed text using:
  1. Comparison with reference answers using similarity metrics
  2. Large Language Model-based evaluation (experimental feature)
  3. Combined scoring methods based on configuration and stored as report



