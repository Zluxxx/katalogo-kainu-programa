import base64
import json
import tempfile
from pathlib import Path

import requests
import streamlit as st
from katalogo_kainu_core import process_catalog, parse_percent

APP_TITLE = "Katalogo kainų programa"
AUTHOR_TEXT = "Autorius Vytautas Žilys"


USAGE_NAMESPACE = "vytautas-zilys-katalogo-kainu-programa"
VISIT_KEY = f"{USAGE_NAMESPACE}/visits"
GENERATE_KEY = f"{USAGE_NAMESPACE}/pdf_generations"
STATS_FILE = Path(__file__).with_name("usage_stats.json")

def _read_local_stats() -> dict:
    try:
        if STATS_FILE.exists():
            data = json.loads(STATS_FILE.read_text(encoding="utf-8"))
            return {
                "visits": int(data.get("visits", 0)),
                "pdf_generations": int(data.get("pdf_generations", 0)),
            }
    except Exception:
        pass
    return {"visits": 0, "pdf_generations": 0}

def _write_local_stats(data: dict) -> None:
    try:
        STATS_FILE.write_text(
            json.dumps({
                "visits": int(data.get("visits", 0)),
                "pdf_generations": int(data.get("pdf_generations", 0)),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass

def _local_hit(field: str) -> int:
    data = _read_local_stats()
    data[field] = int(data.get(field, 0)) + 1
    _write_local_stats(data)
    return data[field]

def _countapi_get(key: str):
    try:
        r = requests.get(f"https://api.countapi.xyz/get/{key}", timeout=8)
        if r.ok:
            return int(r.json().get("value", 0))
    except Exception:
        return None
    return None

def _countapi_hit(key: str):
    try:
        r = requests.get(f"https://api.countapi.xyz/hit/{key}", timeout=8)
        if r.ok:
            return int(r.json().get("value", 0))
    except Exception:
        return None
    return None

def ensure_visit_count_once_per_session():
    if "visit_counted" not in st.session_state:
        st.session_state["visit_counted"] = False
    if not st.session_state["visit_counted"]:
        remote_value = _countapi_hit(VISIT_KEY)
        local_value = _local_hit("visits")
        st.session_state["visit_counted"] = True
        st.session_state["usage_counts"] = {
            "visits": remote_value if remote_value is not None else local_value,
            "pdf_generations": (_countapi_get(GENERATE_KEY) if remote_value is not None else _read_local_stats().get("pdf_generations", 0)),
        }

def load_usage_counts():
    local_data = _read_local_stats()
    remote_visits = _countapi_get(VISIT_KEY)
    remote_generations = _countapi_get(GENERATE_KEY)
    return {
        "visits": remote_visits if remote_visits is not None else local_data.get("visits", 0),
        "pdf_generations": remote_generations if remote_generations is not None else local_data.get("pdf_generations", 0),
    }

ensure_visit_count_once_per_session()

def file_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "generated" not in st.session_state:
    st.session_state.generated = False
if "result_data" not in st.session_state:
    st.session_state.result_data = None
if "usage_counts" not in st.session_state:
    st.session_state["usage_counts"] = load_usage_counts()

st.markdown("""
<style>
.main > div {
    padding-top: 1.2rem;
}
.app-shell {
    max-width: 1100px;
    margin: 0 auto;
}
.hero {
    border: 1px solid rgba(120,120,120,.20);
    border-radius: 22px;
    padding: 24px 28px;
    background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.01));
    margin-bottom: 18px;
}
.hero-row {
    display: flex;
    align-items: center;
    gap: 20px;
}
.hero-logo {
    width: 86px;
    height: 86px;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(120,120,120,.18);
    background: white;
    flex: 0 0 auto;
}
.hero-logo img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
}
.hero h1 {
    font-size: 2rem;
    line-height: 1.1;
    margin: 0 0 6px 0;
}
.muted {
    opacity: .82;
    font-size: .98rem;
}
.panel {
    border: 1px solid rgba(120,120,120,.18);
    border-radius: 22px;
    padding: 18px 18px 10px 18px;
    background: rgba(255,255,255,.015);
    margin-bottom: 16px;
}
.stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0,1fr));
    gap: 12px;
    margin-top: 8px;
    margin-bottom: 6px;
}
.stat-card {
    border: 1px solid rgba(120,120,120,.18);
    border-radius: 18px;
    padding: 14px;
    background: rgba(255,255,255,.02);
}
.stat-label {
    font-size: .86rem;
    opacity: .78;
    margin-bottom: 6px;
}
.stat-value {
    font-size: 1.25rem;
    font-weight: 700;
}
@media (max-width: 900px) {
    .hero-row { flex-direction: column; align-items: flex-start; }
    .stats { grid-template-columns: repeat(2, minmax(0,1fr)); }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-shell">', unsafe_allow_html=True)

logo_path = Path(__file__).with_name("logo.png")
if logo_path.exists():
    logo_html = f'<div class="hero-logo"><img src="data:image/png;base64,{file_to_base64(logo_path)}"></div>'
else:
    logo_html = ""

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-row">
            {logo_html}
            <div>
                <h1>{APP_TITLE}</h1>
                <div class="muted">PDF katalogo kainų generavimas naršyklėje.</div>
                <div class="muted">{AUTHOR_TEXT}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Failų įkėlimas")
    pdf_file = st.file_uploader("PDF katalogas", type=["pdf"], help="Įkelk katalogo PDF failą")
    excel_file = st.file_uploader("Excel kainos", type=["xlsx", "xls"], help="Įkelk kainų lentelę")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Nustatymai")
    c1, c2 = st.columns(2)
    with c1:
        include_contents = st.toggle("Įtraukti turinį", value=False)
        price_label = st.radio("Kainos", ["Su PVM", "Be PVM"], horizontal=True)
        output_name = st.text_input(
            "Išsaugomo PDF pavadinimas",
            value="katalogas_su_kainomis",
            help="Įrašyk norimą galutinio PDF failo pavadinimą be .pdf galūnės",
        )
        bubble_style_label = st.selectbox("Kainos burbulo stilius", ["Klasikinis", "Modernus"], index=0)
        bubble_style = "classic" if bubble_style_label == "Klasikinis" else "modern"
    with c2:
        percent_text = st.text_input(
            "Kainos korekcija (%)",
            value="0",
            help="Teigiamas skaičius = antkainis, neigiamas = nuolaida. Pvz. 10 arba -5,5",
        )
        st.caption("Pvz.: 10 arba -5,5")

    price_mode = "su_pvm" if price_label == "Su PVM" else "be_pvm"
    run = st.button("Generuoti PDF", type="primary", use_container_width=True)
    if st.session_state.generated:
        clear_btn = st.button("Išvalyti rezultatą", use_container_width=True)
        if clear_btn:
            st.session_state.generated = False
            st.session_state.result_data = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Kaip naudoti")
    st.markdown(
        """
        1. Įkelk PDF katalogą  
        2. Įkelk Excel kainų failą  
        3. Įrašyk norimą PDF pavadinimą  
        4. Pasirink kainų režimą, korekciją ir burbulo stilių  
        5. Spausk **Generuoti PDF**  
        6. Atsisiųsk norimus failus
        """
    )
    st.info("Rekomenduojama naudoti `.xlsx` formatą.")
    with st.expander("Naudojimo statistika", expanded=False):
        counts = st.session_state.get("usage_counts") or {}
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Apsilankymai", counts.get("visits") if counts.get("visits") is not None else "—")
        with c2:
            st.metric("Sugeneruoti PDF", counts.get("pdf_generations") if counts.get("pdf_generations") is not None else "—")
        st.caption("Statistika rodoma iš bendro skaitiklio, o jei jis nepasiekiamas – iš vietinės atsarginės apskaitos.")
    st.markdown('</div>', unsafe_allow_html=True)

if run:
    if not pdf_file or not excel_file:
        st.error("Įkelk abu failus: PDF ir Excel.")
        st.stop()

    try:
        percent = parse_percent(percent_text)
    except Exception:
        st.error("Neteisinga korekcijos reikšmė. Pvz. 10 arba -5,5")
        st.stop()

    progress_bar = st.progress(0, text="Pradedama...")
    status_box = st.empty()

    try:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            pdf_path = td / pdf_file.name
            excel_path = td / excel_file.name

            safe_name = (output_name or "katalogas_su_kainomis").strip()
            invalid_chars = '<>:"/\\|?*'
            for ch in invalid_chars:
                safe_name = safe_name.replace(ch, "_")
            if not safe_name:
                safe_name = "katalogas_su_kainomis"
            if safe_name.lower().endswith(".pdf"):
                safe_name = safe_name[:-4].rstrip() or "katalogas_su_kainomis"

            out_pdf = td / f"{safe_name}.pdf"
            report_missing_pdf = td / "excel_kodu_nera_pdf.txt"
            report_missing_excel = td / "pdf_kodu_nera_excel.txt"

            pdf_path.write_bytes(pdf_file.getvalue())
            excel_path.write_bytes(excel_file.getvalue())

            def progress_cb(page_no, total_pages, matched, seen_pdf_codes):
                pct = int((page_no / total_pages) * 100) if total_pages else 0
                progress_bar.progress(
                    pct,
                    text=f"Vykdoma... {pct}% | Puslapiai: {page_no}/{total_pages} | Priskirta kainų: {matched} | PDF kodų: {seen_pdf_codes}"
                )

            result = process_catalog(
                str(pdf_path),
                str(excel_path),
                str(out_pdf),
                str(report_missing_excel),
                str(report_missing_pdf),
                percent,
                progress_cb=progress_cb,
                include_contents=include_contents,
                price_mode=price_mode,
                bubble_style=bubble_style,
            )

            st.session_state.result_data = {
                "result": result,
                "pdf_bytes": out_pdf.read_bytes(),
                "pdf_name": out_pdf.name,
                "missing_pdf_text": report_missing_pdf.read_text(encoding="utf-8", errors="replace"),
                "missing_pdf_name": report_missing_pdf.name,
                "missing_excel_text": report_missing_excel.read_text(encoding="utf-8", errors="replace"),
                "missing_excel_name": report_missing_excel.name,
            }
            remote_generation_value = _countapi_hit(GENERATE_KEY)
            local_generation_value = _local_hit("pdf_generations")
            current_counts = load_usage_counts()
            current_counts["pdf_generations"] = remote_generation_value if remote_generation_value is not None else local_generation_value
            st.session_state["usage_counts"] = current_counts
            st.session_state.generated = True
            st.rerun()

    except Exception as e:
        progress_bar.progress(0, text="Klaida")
        status_box.error(str(e))

if st.session_state.generated and st.session_state.result_data:
    st.session_state["usage_counts"] = load_usage_counts()
    data = st.session_state.result_data
    result = data["result"]

    st.progress(100, text="Baigta")
    st.success("PDF sėkmingai sugeneruotas.")

    st.markdown(
        f"""
        <div class="stats">
            <div class="stat-card"><div class="stat-label">Naudotas Excel lapas</div><div class="stat-value">{result['sheet_name']}</div></div>
            <div class="stat-card"><div class="stat-label">Priskirta kainų</div><div class="stat-value">{result['matched']}</div></div>
            <div class="stat-card"><div class="stat-label">Excel kodų nėra PDF</div><div class="stat-value">{result['missing_in_pdf']}</div></div>
            <div class="stat-card"><div class="stat-label">PDF kodų nėra Excel</div><div class="stat-value">{result['missing_in_excel']}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Parsisiuntimai")

    cols = st.columns(3)
    downloads = [
        ("PDF", data["pdf_bytes"], data["pdf_name"], "application/pdf"),
        ("Excel kodų nėra PDF", data["missing_pdf_text"], data["missing_pdf_name"], "text/plain"),
        ("PDF kodų nėra Excel", data["missing_excel_text"], data["missing_excel_name"], "text/plain"),
    ]

    for col, item in zip(cols, downloads):
        label, file_data, fname, mime = item
        with col:
            st.download_button(
                f"Atsisiųsti: {label}",
                data=file_data,
                file_name=fname,
                mime=mime,
                use_container_width=True,
            )

    with st.expander("Išsami suvestinė", expanded=False):
        st.json({
            "Naudotas Excel lapas": result["sheet_name"],
            "Kainos stulpelis": result["price_col"],
            "Priskirta kainų": result["matched"],
            "Excel kodų nėra PDF": result["missing_in_pdf"],
            "PDF kodų nėra Excel": result["missing_in_excel"],
            "Rasta PDF kodų": result["seen_pdf_codes"],
            "Puslapių": result["total_pages"],
            "Galutinis dydis (MB)": result["final_size_mb"],
        }, expanded=False)

st.markdown('</div>', unsafe_allow_html=True)
