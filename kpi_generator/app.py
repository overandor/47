import os
import json
import time
import threading
import queue
import pandas as pd
import gradio as gr
from groq import Groq

GROQ_MODEL = "llama3-70b-8192"
MAX_KPI_HISTORY = 500

kpi_store: list[dict] = []
generation_active = False
gen_thread: threading.Thread | None = None
kpi_queue: queue.Queue = queue.Queue()


def _build_dataset_summary(df: pd.DataFrame) -> str:
    lines = [
        f"Rows: {len(df)}, Columns: {len(df.columns)}",
        f"Columns: {', '.join(df.columns.tolist())}",
        "",
        "Data types:",
    ]
    for col, dtype in df.dtypes.items():
        lines.append(f"  {col}: {dtype}")
    lines.append("")
    lines.append("Sample statistics (numeric columns):")
    try:
        stats = df.describe().to_string()
        lines.append(stats)
    except Exception:
        lines.append("  (no numeric columns)")
    lines.append("")
    lines.append("First 3 rows:")
    lines.append(df.head(3).to_string())
    return "\n".join(lines)


def _parse_kpis_from_response(text: str, batch_num: int) -> list[dict]:
    kpis = []
    lines = text.strip().split("\n")
    current: dict | None = None
    for line in lines:
        line = line.strip()
        if not line:
            if current:
                kpis.append(current)
                current = None
            continue
        if line.startswith(("KPI", "**KPI", "###", "##")) or (
            len(line) < 80 and ":" not in line and not line.startswith("-")
        ):
            if current:
                kpis.append(current)
            current = {
                "id": f"kpi-{batch_num}-{len(kpis)+1}",
                "name": line.lstrip("#* "),
                "formula": "",
                "target": "",
                "rationale": "",
                "batch": batch_num,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        elif current:
            lower = line.lower()
            if lower.startswith("formula") or lower.startswith("calculation"):
                current["formula"] = line.split(":", 1)[-1].strip()
            elif lower.startswith("target") or lower.startswith("goal"):
                current["target"] = line.split(":", 1)[-1].strip()
            elif lower.startswith("rationale") or lower.startswith("reason") or lower.startswith("why"):
                current["rationale"] = line.split(":", 1)[-1].strip()
    if current:
        kpis.append(current)

    # fallback: treat every non-empty line as a KPI name if nothing parsed
    if not kpis:
        for i, line in enumerate(lines):
            line = line.strip("*#- \t")
            if len(line) > 5:
                kpis.append({
                    "id": f"kpi-{batch_num}-{i+1}",
                    "name": line,
                    "formula": "",
                    "target": "",
                    "rationale": "",
                    "batch": batch_num,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                })
    return kpis


def _generate_loop(
    api_key: str,
    dataset_summary: str,
    already_generated: list[str],
    batch_size: int,
    delay: float,
    stop_event: threading.Event,
) -> None:
    client = Groq(api_key=api_key)
    batch_num = 0

    while not stop_event.is_set():
        batch_num += 1
        existing_names = ", ".join(already_generated[-60:]) if already_generated else "none yet"

        prompt = f"""You are a data analytics expert. Given the dataset below, generate exactly {batch_size} NEW, unique KPIs that have NOT been listed in the 'already generated' list.

DATASET SUMMARY:
{dataset_summary}

ALREADY GENERATED KPIs (do not repeat these):
{existing_names}

For each KPI provide:
KPI Name
Formula: <how to calculate it from the dataset columns>
Target: <a realistic benchmark or goal>
Rationale: <why this KPI matters for this dataset>

Separate each KPI with a blank line. Be creative — explore operational, financial, quality, growth, efficiency, and predictive angles."""

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.9,
            )
            text = response.choices[0].message.content or ""
            new_kpis = _parse_kpis_from_response(text, batch_num)
            for kpi in new_kpis:
                already_generated.append(kpi["name"])
                kpi_queue.put(kpi)
        except Exception as exc:
            kpi_queue.put({"error": str(exc), "batch": batch_num})

        stop_event.wait(timeout=delay)


def load_dataset(file_obj) -> tuple[str, str]:
    if file_obj is None:
        return "", "No file uploaded."
    try:
        path = file_obj.name
        if path.endswith(".csv"):
            df = pd.read_csv(path)
        elif path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(path)
        elif path.endswith(".json"):
            df = pd.read_json(path)
        elif path.endswith(".parquet"):
            df = pd.read_parquet(path)
        else:
            df = pd.read_csv(path)
        summary = _build_dataset_summary(df)
        return summary, f"Loaded {len(df)} rows × {len(df.columns)} columns from {os.path.basename(path)}"
    except Exception as exc:
        return "", f"Error loading file: {exc}"


def start_generation(
    api_key: str,
    dataset_summary: str,
    batch_size: int,
    delay_seconds: float,
) -> str:
    global generation_active, gen_thread, kpi_store

    if not api_key.strip():
        return "Please enter a Groq API key."
    if not dataset_summary.strip():
        return "Please load a dataset first."
    if generation_active:
        return "Generation is already running."

    kpi_store.clear()
    while not kpi_queue.empty():
        kpi_queue.get_nowait()

    stop_event = threading.Event()
    generation_active = True

    already_generated: list[str] = []

    def _run():
        global generation_active
        try:
            _generate_loop(
                api_key=api_key,
                dataset_summary=dataset_summary,
                already_generated=already_generated,
                batch_size=int(batch_size),
                delay=float(delay_seconds),
                stop_event=stop_event,
            )
        finally:
            generation_active = False

    gen_thread = threading.Thread(target=_run, daemon=True)
    gen_thread._stop_event = stop_event  # type: ignore[attr-defined]
    gen_thread.start()
    return "Generation started. KPIs will appear in the table below."


def stop_generation() -> str:
    global generation_active, gen_thread
    if gen_thread and hasattr(gen_thread, "_stop_event"):
        gen_thread._stop_event.set()
    generation_active = False
    return "Generation stopped."


def _drain_queue() -> None:
    while not kpi_queue.empty():
        item = kpi_queue.get_nowait()
        if "error" not in item:
            kpi_store.append(item)
            if len(kpi_store) > MAX_KPI_HISTORY:
                kpi_store.pop(0)


def refresh_table() -> tuple[list[list], str]:
    _drain_queue()
    rows = [
        [
            k.get("id", ""),
            k.get("batch", ""),
            k.get("name", ""),
            k.get("formula", ""),
            k.get("target", ""),
            k.get("rationale", ""),
            k.get("timestamp", ""),
        ]
        for k in kpi_store
    ]
    status = (
        f"Running — {len(kpi_store)} KPIs generated so far"
        if generation_active
        else f"Stopped — {len(kpi_store)} KPIs total"
    )
    return rows, status


def export_kpis() -> str | None:
    _drain_queue()
    if not kpi_store:
        return None
    path = "/tmp/kpis_export.json"
    with open(path, "w") as f:
        json.dump(kpi_store, f, indent=2)
    return path


def export_csv() -> str | None:
    _drain_queue()
    if not kpi_store:
        return None
    path = "/tmp/kpis_export.csv"
    pd.DataFrame(kpi_store).to_csv(path, index=False)
    return path


# ── UI ──────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Infinite KPI Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Infinite KPI Generator\nPowered by Groq API (LLaMA 3 70B). Upload a dataset, enter your API key, and let the system generate KPIs indefinitely.")

    with gr.Row():
        with gr.Column(scale=1):
            api_key_input = gr.Textbox(
                label="Groq API Key",
                placeholder="gsk_...",
                type="password",
            )
            file_upload = gr.File(
                label="Upload Dataset (CSV / Excel / JSON / Parquet)",
                file_types=[".csv", ".xlsx", ".xls", ".json", ".parquet"],
            )
            load_btn = gr.Button("Load Dataset", variant="secondary")
            load_status = gr.Textbox(label="Load Status", interactive=False)

            with gr.Row():
                batch_size = gr.Slider(
                    minimum=1, maximum=20, value=5, step=1,
                    label="KPIs per batch",
                )
                delay_slider = gr.Slider(
                    minimum=2, maximum=60, value=10, step=1,
                    label="Delay between batches (seconds)",
                )

            with gr.Row():
                start_btn = gr.Button("Start Infinite Generation", variant="primary")
                stop_btn = gr.Button("Stop", variant="stop")

            gen_status = gr.Textbox(label="Generation Status", interactive=False)

        with gr.Column(scale=2):
            dataset_summary_box = gr.Textbox(
                label="Dataset Summary",
                lines=10,
                interactive=False,
            )

    gr.Markdown("## Generated KPIs")

    with gr.Row():
        refresh_btn = gr.Button("Refresh Table")
        export_json_btn = gr.Button("Export JSON")
        export_csv_btn = gr.Button("Export CSV")

    table_status = gr.Textbox(label="Table Status", interactive=False)

    kpi_table = gr.Dataframe(
        headers=["ID", "Batch", "Name", "Formula", "Target", "Rationale", "Timestamp"],
        datatype=["str", "number", "str", "str", "str", "str", "str"],
        interactive=False,
        wrap=True,
        label="KPI Table",
    )

    json_file = gr.File(label="JSON Export", interactive=False)
    csv_file = gr.File(label="CSV Export", interactive=False)

    # ── event wiring ──────────────────────────────────────────────────────

    load_btn.click(
        fn=load_dataset,
        inputs=[file_upload],
        outputs=[dataset_summary_box, load_status],
    )

    start_btn.click(
        fn=start_generation,
        inputs=[api_key_input, dataset_summary_box, batch_size, delay_slider],
        outputs=[gen_status],
    )

    stop_btn.click(fn=stop_generation, outputs=[gen_status])

    refresh_btn.click(fn=refresh_table, outputs=[kpi_table, table_status])

    export_json_btn.click(fn=export_kpis, outputs=[json_file])
    export_csv_btn.click(fn=export_csv, outputs=[csv_file])

    # auto-refresh every 8 seconds while the page is open
    demo.load(fn=refresh_table, outputs=[kpi_table, table_status], every=8)


if __name__ == "__main__":
    demo.launch()
