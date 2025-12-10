# SynAPX - Autonomous Insurance Claims Processing Agent

## 📺 Demo Video

Watch the full demonstration: **[View Demo on Loom](https://www.loom.com/share/5381bc2001aa4757ae7b4e9a5019605a)**

---

## 🎯 What is This?

An autonomous agent that processes insurance FNOL (First Notice of Loss) documents. It:

- **Extracts** key fields from PDF/TXT documents using AI
- **Validates** data completeness (checks 13 mandatory fields)
- **Routes** claims to appropriate workflows based on business rules
- **Explains** routing decisions with clear reasoning

---

## 🔄 How It Works

```
📄 Upload Document (PDF/TXT)
      ↓
🤖 AI Extraction (Google Gemini + Pattern Matching Fallback)
      ↓
✅ Validation (Check Missing Fields)
      ↓
🔀 Smart Routing (Apply Business Rules)
      ↓
📊 JSON Output (Results + Reasoning)
```

**Routing Rules:**
1. Missing mandatory fields → Manual Review
2. Fraud keywords detected → Investigation Flag
3. Personal injury claim → Specialist Queue
4. Damage < $25,000 & complete → Fast-track
5. High-value claim → Manual Review

---

## 🚀 Quick Start

### Clone Repository

```bash
git clone https://github.com/Ganesh-Sonawane-IIITV/synapx.git
cd synapx
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python api.py
```

Then open **http://localhost:8000** in your browser.

---

## ⚙️ Configuration (Optional)

For best extraction quality, set up Gemini API key:

**Option 1: Web UI (Easiest)**
1. Click ⚙️ settings icon in web interface
2. Enter your API key
3. Click "Save"

**Option 2: Environment File**
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Get free API key: https://makersuite.google.com/app/apikey

> **Note:** Application works without API key using pattern-based fallback extraction!

---

## 📁 Project Structure

```
synapx/
├── src/               # Source code
│   ├── agent.py       # Main orchestrator
│   ├── extractor.py   # AI extraction
│   ├── validator.py   # Validation
│   ├── router.py      # Routing logic
│   └── utils.py       # Utilities
├── web/               # Web interface
├── tests/             # Test suite
├── api.py             # FastAPI server
└── README.md
```

---

## 💻 Usage

### Web Interface
```bash
python api.py
# Open: http://localhost:8000
```

### Command Line
```bash
# Process single document
python src/agent.py document.txt

# Process with output
python src/agent.py document.pdf --output result.json
```

### Python API
```python
from src.agent import ClaimsProcessingAgent

agent = ClaimsProcessingAgent()
result = agent.process_claim("document.pdf")

print(result['recommendedRoute'])
print(result['reasoning'])
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Made with ❤️ for intelligent claims processing
