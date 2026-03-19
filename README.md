# Supply Chain AI Copilot..

A Streamlit web application that lets supply chain managers analyze order shipment data and ask operational questions in plain English. Powered by Groq AI (free tier).

---

## Demo

The app has 4 tabs:

- **Dashboard** — KPI metrics and 6 interactive Plotly charts
- **Data Table** — Full dataset with computed metrics and warehouse/product summaries
- **AI Chat** — Ask natural language questions about your data with full conversation history
- **AI Insights** — One-click AI-generated executive overview, bottleneck analysis, and recommendations

---

## Tech Stack

- Python 3.10+
- Streamlit — web interface
- Pandas — data processing
- Plotly — interactive charts
- Groq API (llama-3.3-70b-versatile) — AI question answering
- python-dotenv — environment variable management

---

## Project Structure

```
supply_chain_copilot/
    app.py              Main Streamlit application (entry point)
    data_processor.py   CSV loading, metric computation, aggregations
    ai_engine.py        Groq API integration (easy Claude swap)
    charts.py           Plotly chart generation
    orders.csv          Sample dataset 1 (40 orders, 3 warehouses)
    orders_large.csv    Sample dataset 2 (80 orders, 5 warehouses)
    requirements.txt    Python dependencies
    .env.example        Template for environment variables
    test_api.py         Script to verify your API key works
    README.md           This file
```

---

## Setup and Run

### Step 1 - Clone the repository

```
git clone https://github.com/your-username/supply_chain_copilot.git
cd supply_chain_copilot
```

### Step 2 - Create and activate a virtual environment

```
python -m venv venv
```

Windows:
```
venv\Scripts\activate
```

Mac/Linux:
```
source venv/bin/activate
```

### Step 3 - Install dependencies

```
pip install -r requirements.txt
```

### Step 4 - Get a free Groq API key

1. Go to https://console.groq.com
2. Sign up (no credit card required)
3. Click API Keys in the left sidebar
4. Click Create API Key
5. Copy the key starting with gsk_

### Step 5 - Set your API key

Windows PowerShell (recommended — avoids encoding issues):
```
Set-Content -Path .env -Value "GROQ_API_KEY=your_key_here" -Encoding UTF8
```

Mac/Linux:
```
cp .env.example .env
```
Then open .env and replace your_groq_api_key_here with your actual key.

Alternatively, set it directly in the terminal for the current session:

Windows:
```
$env:GROQ_API_KEY = "your_key_here"
```

Mac/Linux:
```
export GROQ_API_KEY=your_key_here
```

### Step 6 - Test your API key (optional but recommended)

```
python test_api.py
```

### Step 7 - Run the app

```
streamlit run app.py
```

Open your browser at http://localhost:8501

---

## CSV Format

Upload your own CSV from the sidebar. Required columns:

| Column        | Type   | Example     |
|---------------|--------|-------------|
| Order_ID      | string | ORD001      |
| Product       | string | Laptop      |
| Warehouse     | string | Warehouse_A |
| Order_Date    | date   | 2024-01-01  |
| Ship_Date     | date   | 2024-01-03  |
| Delivery_Date | date   | 2024-01-07  |
| Quantity      | int    | 10          |
| Status        | string | Delivered   |

Dates must be in YYYY-MM-DD format.

Computed columns added automatically:
- Processing_Time_Days = Ship_Date - Order_Date
- Shipping_Delay_Days  = Delivery_Date - Ship_Date
- Total_Lead_Time_Days = Delivery_Date - Order_Date

---

## Example Questions to Ask

- Which warehouse has the highest shipping delay?
- Which product ships fastest on average?
- What is the average delay per warehouse?
- Which orders were delayed more than 3 days?
- Which warehouse handles the most orders?
- What is the worst performing product by lead time?
- Compare processing times across all warehouses.
- Which product has the most delayed orders?

---

## Switching to Claude API

When you are ready to use Anthropic Claude instead of Groq:

1. Get an API key at https://console.anthropic.com

2. Install the Anthropic library:
```
pip install anthropic
```

3. Open ai_engine.py and replace the call_llm() function body with:
```python
import anthropic
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    system=system,
    messages=messages,
)
return response.content[0].text
```

4. Add your key to .env:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
```

No other files need to change.

---

## Known Limitation

The AI receives a text summary of aggregated metrics rather than raw rows. This means it cannot answer highly specific row-level queries like "list every order from Warehouse A on January 15th" without a vector database (RAG) layer. For operational summaries, trend questions, and warehouse/product comparisons, the summary approach is accurate and sufficient.

---

## Evaluation Criteria (Assignment)

| Category               | Notes                                                         |
|------------------------|---------------------------------------------------------------|
| Problem solving        | Computes processing time, delay, lead time; flags slow orders |
| Code quality           | Modular — separate files for data, AI, charts, and UI         |
| AI usage               | Natural language Q&A + insight generation via Groq/Claude     |
| Creativity             | Dashboard, heatmap, trend chart, AI insights tab              |
| Clarity of explanation | README covers setup, format, swap guide, and limitations      |
