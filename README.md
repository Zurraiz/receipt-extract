# DocExtract — AI Document Data Extraction

Extract structured data from invoices, receipts, purchase orders, bank statements, or any custom document type using AI vision.

## Features

- **4 built-in schemas** — Invoice, Receipt, Purchase Order, Bank Statement
- **Custom schema** — define any fields you want extracted
- **Swappable AI backend** — Gemini (free) for demo, Claude/OpenAI for production
- **Export** — JSON and CSV download
- **Drag and drop** — PDF and image support

## Local Setup

```bash
# 1. Clone and enter directory
git clone <your-repo>
cd invoice-extractor

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key (get free key at https://aistudio.google.com)
export GEMINI_API_KEY=your_key_here
# Windows: set GEMINI_API_KEY=your_key_here

# 5. Run
python app.py
# Open http://localhost:7860
```

## Switching AI Providers

Change the `AI_PROVIDER` environment variable — no code changes needed:

```bash
# Free (default)
export AI_PROVIDER=gemini
export GEMINI_API_KEY=your_key

# Paid — Claude
export AI_PROVIDER=claude
export ANTHROPIC_API_KEY=your_key

# Paid — OpenAI
export AI_PROVIDER=openai
export OPENAI_API_KEY=your_key
```

Also uncomment the relevant line in `requirements.txt` and `pip install -r requirements.txt`.

## Deploy to Hugging Face Spaces

1. Create a new Space → SDK: **Docker** (or Gradio if you prefer)
2. Push this repo
3. Add `GEMINI_API_KEY` in **Settings → Secrets**

For Docker deployment add this `Dockerfile` to the root:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

## Adding a New Document Type (Client Customization)

Open `extractors/schemas.py` and add a new entry to `SCHEMAS`:

```python
"medical_bill": {
    "label": "Medical Bill",
    "fields": {
        "patient_name":   "Full name of the patient",
        "provider":       "Hospital or clinic name",
        "date_of_service": "Date of the medical service",
        "procedure_codes": "List of procedure/CPT codes",
        "total_charges":  "Total amount charged",
        "insurance_paid": "Amount covered by insurance",
        "patient_due":    "Amount the patient owes"
    }
}
```

That's it — the UI and extraction logic pick it up automatically.

## Project Structure

```
invoice-extractor/
├── app.py                          # Flask server + API routes
├── requirements.txt
├── extractors/
│   ├── ai_client.py                # AI backend (swap provider here)
│   ├── schemas.py                  # Document field definitions
│   └── document_processor.py      # PDF/image preprocessing
└── templates/
    └── index.html                  # Frontend UI
```
