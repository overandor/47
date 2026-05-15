# Infinite KPI Generator

A Hugging Face Spaces app that uses the **Groq API** (LLaMA 3 70B) to generate an unlimited stream of KPIs from any uploaded dataset.

## How it works

1. Upload a dataset (CSV, Excel, JSON, or Parquet).
2. Enter your [Groq API key](https://console.groq.com).
3. Configure batch size and delay between batches.
4. Click **Start Infinite Generation**.
5. The app runs a background thread that calls Groq in a loop, each time asking for fresh KPIs that have not been generated before.
6. KPIs are shown in a live table; click **Refresh Table** or wait for the 8-second auto-refresh.
7. Export results as JSON or CSV at any time.

## KPI structure

| Field      | Description                                      |
|------------|--------------------------------------------------|
| ID         | Unique identifier (batch-sequence)               |
| Batch      | Which generation batch produced this KPI         |
| Name       | KPI name                                         |
| Formula    | How to calculate it from the dataset columns     |
| Target     | Realistic benchmark or goal                      |
| Rationale  | Why this KPI matters for the dataset             |
| Timestamp  | When it was generated                            |

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

## Deploy to Hugging Face Spaces

1. Create a new Space with the **Gradio** SDK.
2. Push this directory as the Space repository.
3. Add `GROQ_API_KEY` as a Space secret if you want a server-side default key (optional — users can also enter their own key in the UI).
