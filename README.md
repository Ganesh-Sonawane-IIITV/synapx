# 🚀 SynAPX - Autonomous Insurance Claims Processing Agent

> AI-powered intelligent FNOL document processing with automatic field extraction, validation, and routing

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-success.svg)]()

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Demo](#demo)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [How to Run](#how-to-run)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Routing Rules](#routing-rules)
- [Sample Documents](#sample-documents)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**SynAPX** is an autonomous agent that processes First Notice of Loss (FNOL) insurance documents, extracting key information, validating data completeness, and intelligently routing claims to appropriate workflows.

### What It Does

1. **📄 Extracts** key fields from FNOL documents (PDF/TXT)
2. **✅ Validates** data completeness and consistency
3. **🔀 Routes** claims based on intelligent business rules
4. **💡 Explains** routing decisions with clear reasoning

### Why It's Special

- **🤖 AI-Powered**: Uses Google Gemini for intelligent extraction
- **🔄 Zero-Config**: Falls back to pattern-based extraction automatically
- **🌐 Multiple Interfaces**: Web UI, REST API, CLI, Python module
- **⚡ Production-Ready**: Error handling, validation, comprehensive testing

---

## ✨ Key Features

### Core Capabilities

✅ **Multi-Format Support**
- Processes PDF and TXT documents
- Automatic format detection
- Robust text extraction

✅ **Intelligent Field Extraction**
- 15+ fields extracted automatically
- AI-powered understanding (Gemini)
- Pattern-based fallback (no API key needed)

✅ **Comprehensive Validation**
- 13 mandatory fields checked
- Missing field detection
- Data consistency validation

✅ **Smart Routing**
- 4 routing workflows implemented
- Priority-based rule application
- Clear reasoning for every decision

✅ **User-Friendly Interfaces**
- **Web UI**: Beautiful, responsive interface
- **REST API**: Full programmatic access
- **CLI**: Command-line batch processing
- **Python API**: Direct module integration

✅ **Production Features**
- Automatic fallback extraction
- UI-based configuration
- Comprehensive error handling
- Extensive documentation
- Automated testing

---

## 🎬 Demo

### Web Interface

The application provides a modern, intuitive web interface:

1. **Upload Documents**: Drag & drop or click to browse
2. **Process Instantly**: AI extraction in 2-5 seconds
3. **View Results**: Routing decision, extracted fields, JSON output
4. **Configure Settings**: Set API key from UI (no file editing!)

### Command Line

```bash
# Process single document
python src/agent.py sample_documents/claim_001.txt

# Process all sample documents
python src/agent.py --all

# Save output to file
python src/agent.py sample_documents/claim_001.txt --output result.json
```

---

## ⚡ Quick Start

Get up and running in 3 minutes:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Set up Gemini API key for best quality
# Get free key from: https://makersuite.google.com/app/apikey
echo "GEMINI_API_KEY=your_api_key_here" > .env

# 3. Start the application
python api.py
```

**That's it!** Open http://localhost:8000 in your browser.

> **Note:** The application works even without a Gemini API key using our fallback extractor!

---

## 🛠️ Detailed Setup

### Prerequisites

- **Python 3.8 or higher**
- **Internet connection** (for AI API, optional)
- **pip** (Python package manager)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd synapx
```

#### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-generativeai` - Gemini AI SDK
- `PyPDF2` - PDF processing
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `pytest` - Testing framework

#### 4. Configure API Key (Optional but Recommended)

**Option A: Using .env File**

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_actual_api_key_here
```

**Option B: Using Web UI (Easiest)**

1. Start the application: `python api.py`
2. Open http://localhost:8000
3. Click the ⚙️ settings icon
4. Enter your API key
5. Click "Save API Key"

**Get Free API Key:**
Visit https://makersuite.google.com/app/apikey (no credit card required)

#### 5. Verify Setup

```bash
python setup_check.py
```

You should see all ✅ checks pass!

---

## 🚀 How to Run

### Method 1: Web Interface (Recommended)

**Start the server:**

```bash
python api.py
```

You'll see:
```
╔═══════════════════════════════════════════════════════════╗
║  Insurance Claims Processing Agent API                   ║
╚═══════════════════════════════════════════════════════════╝

🚀 Server starting...

📍 API URL: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
🌐 Web Interface: http://localhost:8000
```

**Then:**
1. Open your browser to http://localhost:8000
2. Upload a document or click "Try Sample Document"
3. Click "Process Document"
4. View the results!

**To stop:** Press `Ctrl+C`

### Method 2: Command Line Interface

**Process a single document:**

```bash
python src/agent.py sample_documents/claim_001.txt
```

**Process all sample documents:**

```bash
python src/agent.py --all
```

**Save output to JSON file:**

```bash
python src/agent.py sample_documents/claim_001.txt --output result.json
```

**Process with custom output directory:**

```bash
python src/agent.py --all --output-dir ./results
```

### Method 3: Python API

```python
from src.agent import ClaimsProcessingAgent

# Initialize agent
agent = ClaimsProcessingAgent()

# Process a document
result = agent.process_claim("sample_documents/claim_001.txt")

# Access results
print(f"Route: {result['recommendedRoute']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Missing Fields: {len(result['missingFields'])}")

# Print extracted fields
for field, value in result['extractedFields'].items():
    print(f"{field}: {value}")
```

### Method 4: REST API

**Start the server:**

```bash
python api.py
```

**Send requests:**

```bash
# Upload and process document
curl -X POST "http://localhost:8000/process" \
  -F "file=@sample_documents/claim_001.txt"

# Check health
curl http://localhost:8000/health

# Get routing rules
curl http://localhost:8000/routing-rules

# Get configuration status
curl http://localhost:8000/config
```

**API Documentation:**
Visit http://localhost:8000/docs for interactive Swagger documentation

---

## 📚 Usage Examples

### Example 1: Basic Document Processing

```bash
# Start server
python api.py

# In browser: http://localhost:8000
# 1. Click "Try Sample Document"
# 2. Click "Process Document"
# 3. View results
```

### Example 2: Batch Processing

```bash
# Process all sample documents
python src/agent.py --all

# Output:
# - Routes all 5 documents
# - Shows routing distribution
# - Displays summary statistics
```

### Example 3: Custom Integration

```python
from src.agent import ClaimsProcessingAgent
import json

# Initialize with custom API key
agent = ClaimsProcessingAgent(api_key="your_key")

# Process multiple documents
documents = ["claim_001.txt", "claim_002.txt", "claim_003.txt"]

results = []
for doc in documents:
    result = agent.process_claim(f"sample_documents/{doc}")
    results.append(result)
    
# Save all results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Example 4: API Integration

```javascript
// JavaScript example for web integration
async function processDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/process', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log('Route:', result.recommendedRoute);
  console.log('Reasoning:', result.reasoning);
  return result;
}
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│           CLIENT INTERFACES                 │
│  Web UI  │  CLI  │  Python API  │  REST API │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  ClaimsProcessingAgent  │
         │     (Orchestrator)      │
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌─────▼──────┐  ┌───▼────┐
│ Field  │  │   Field    │  │ Claim  │
│Extractor│  │ Validator  │  │ Router │
└───┬────┘  └────────────┘  └────────┘
    │
┌───▼───────────────┐
│ Gemini AI         │  (Primary)
│ Pattern Matching  │  (Fallback)
└───────────────────┘
```

### Data Flow

1. **Document Upload** → Received via Web UI, CLI, or API
2. **Text Extraction** → PDF/TXT → Plain text
3. **Field Extraction** → AI/Pattern parsing → Structured data
4. **Validation** → Check mandatory fields
5. **Routing** → Apply business rules → Routing decision
6. **Output** → JSON response with reasoning

### Key Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| `agent.py` | Main orchestrator, coordinates all components | 226 |
| `extractor.py` | AI + pattern-based field extraction | 382 |
| `validator.py` | Data validation and completeness checks | 109 |
| `router.py` | Routing logic and business rules | 159 |
| `utils.py` | PDF/TXT reading, date parsing, utilities | 184 |
| `api.py` | FastAPI server, REST endpoints | 281 |

---

## 🔀 Routing Rules

The system applies routing rules in priority order:

### 1. Missing Fields (Highest Priority)
**Rule:** If any mandatory field is missing  
**Route:** Manual Review  
**Reasoning:** "Missing mandatory fields require human review"

### 2. Fraud Indicators
**Rule:** Description contains fraud keywords  
**Keywords:** fraud, fraudulent, inconsistent, staged, suspicious, fabricated, false claim, deceptive  
**Route:** Investigation Flag  
**Reasoning:** "Potential fraud indicators detected"

### 3. Injury Claims
**Rule:** Claim type indicates personal injury  
**Types:** Injury, Personal Injury, Bodily Injury  
**Route:** Specialist Queue  
**Reasoning:** "Injury claims require specialist review"

### 4. Damage Amount
**Rule:** Estimated damage < $25,000 and all fields present  
**Route:** Fast-track  
**Reasoning:** "Low-value claim with complete information"

**Rule:** Estimated damage ≥ $25,000  
**Route:** Manual Review  
**Reasoning:** "High-value claim requires manual review"

---

## 📄 Sample Documents

The project includes 5 comprehensive sample FNOL documents:

| File | Scenario | Route | Details |
|------|----------|-------|---------|
| `claim_001.txt` | Standard auto collision | Fast-track | Complete, $15K damage |
| `claim_002.txt` | High-value property damage | Manual Review | Complete, $75K damage |
| `claim_003.txt` | Suspicious claim | Investigation Flag | Contains fraud keywords |
| `claim_004.txt` | Personal injury | Specialist Queue | Bodily injury claim |
| `claim_005.txt` | Incomplete submission | Manual Review | Missing multiple fields |

### Testing All Scenarios

```bash
# Test each routing scenario
python src/agent.py sample_documents/claim_001.txt  # Fast-track
python src/agent.py sample_documents/claim_002.txt  # Manual Review (high value)
python src/agent.py sample_documents/claim_003.txt  # Investigation Flag
python src/agent.py sample_documents/claim_004.txt  # Specialist Queue
python src/agent.py sample_documents/claim_005.txt  # Manual Review (missing)
```

---

## 📡 API Documentation

### Endpoints

#### POST `/process`
Process an FNOL document

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF or TXT)

**Response:**
```json
{
  "extractedFields": {
    "policyNumber": "POL-2023-123456",
    "policyholderName": "John Doe",
    ...
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "All mandatory fields present..."
}
```

#### GET `/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Agent is ready"
}
```

#### GET `/routing-rules`
Get routing rules summary

**Response:**
```json
{
  "rules": [...],
  "fast_track_threshold": 25000
}
```

#### GET `/config`
Get current configuration

**Response:**
```json
{
  "has_api_key": true,
  "using_gemini": true,
  "using_fallback": false
}
```

#### POST `/config/api-key`
Configure Gemini API key

**Request:**
```json
{
  "api_key": "your_api_key_here"
}
```

#### DELETE `/config/api-key`
Remove API key and use fallback

**Full Documentation:**
Visit http://localhost:8000/docs when server is running

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "GEMINI_API_KEY not found"
**Solution:**
```bash
# Option 1: Use .env file
echo "GEMINI_API_KEY=your_key" > .env

# Option 2: Use web UI
# Click ⚙️ settings → Enter API key → Save

# Option 3: Continue without API key (uses fallback)
# Just start using it - no action needed!
```

#### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Option 1: Stop other program using port 8000

# Option 2: Use different port
# Edit .env:
# API_PORT=8001
```

#### Issue: "Processing taking too long"
**Cause:** First AI request initializes model (8-12 seconds)  
**Solution:** Subsequent requests are much faster (2-5 seconds)

#### Issue: "PDF processing failed"
**Solution:**
```bash
# Ensure PyPDF2 is installed
pip install PyPDF2

# Try with sample TXT first
python src/agent.py sample_documents/claim_001.txt
```

### Getting Help

1. Run setup verification: `python setup_check.py`
2. Check server health: http://localhost:8000/health
3. View logs in terminal
4. Check `TROUBLESHOOTING.md` for detailed guides

---

## 📁 Project Structure

```
synapx/
├── README.md                    # This file
├── QUICKSTART.md               # Fast start guide
├── ARCHITECTURE.md             # Detailed architecture
├── ASSESSMENT_COMPLIANCE.md    # Requirements checklist
├── LICENSE                     # MIT License
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git exclusions
│
├── api.py                      # FastAPI server
├── setup_check.py              # Setup verification
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── agent.py                # Main orchestrator
│   ├── extractor.py            # AI extraction
│   ├── validator.py            # Validation logic
│   ├── router.py               # Routing rules
│   └── utils.py                # Utilities
│
├── sample_documents/           # Test documents
│   ├── claim_001.txt
│   ├── claim_002.txt
│   ├── claim_003.txt
│   ├── claim_004.txt
│   └── claim_005.txt
│
├── tests/                      # Test suite
│   └── test_agent.py
│
└── web/                        # Web interface
    ├── index.html
    ├── styles.css
    └── script.js
```

---

## 🧪 Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Tests

```bash
# Test routing logic
python -m pytest tests/test_agent.py::test_routing -v

# Test validation
python -m pytest tests/test_agent.py::test_validation -v
```

### Manual Testing

```bash
# Test with all sample documents
python src/agent.py --all

# Expected output: 5 documents processed with different routes
```

---

## 🚀 Deployment

### Local Development
```bash
python api.py
```

### Production Deployment

**Recommended:** Use a production ASGI server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Environment Variables:**
```bash
export GEMINI_API_KEY=your_production_key
export API_HOST=0.0.0.0
export API_PORT=8000
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone and setup
git clone <repo-url>
cd synapx
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Start development server
python api.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent document processing
- **FastAPI** for the excellent web framework
- **PyPDF2** for PDF processing capabilities

---

## 📞 Support

For questions or issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [API Documentation](#api-documentation)
3. Run `python setup_check.py` to verify setup
4. Check existing issues on GitHub

---

## 🎯 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Get API key: https://makersuite.google.com/app/apikey (optional)
3. ✅ Start server: `python api.py`
4. ✅ Open http://localhost:8000
5. ✅ Process your first document!

---

**Made with ❤️ for intelligent claims processing**

*Last updated: December 2024*
