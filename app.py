"""
NOH Clinical Vault
Secure document repository for Network One Health clinical governance documents.
Includes the Clinical Operations Manual, 11 SOPs, and 10 QRCs.
"""

import streamlit as st
import requests
from auth import require_auth, logout_button, _get_client

st.set_page_config(
    page_title="NOH Clinical Vault",
    page_icon="\U0001f3e5",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
    html, body, [class*="css"], .stMarkdown, .stText,
    h1, h2, h3, h4, h5, h6, p, span, div, td, th, li {
        font-family: Arial, Helvetica, sans-serif !important;
    }
    .brand-header {
        background: linear-gradient(135deg, #40887d 0%, #2d6159 100%);
        color: white; padding: 1.25rem 2rem; border-radius: 10px;
        margin-bottom: 1.5rem; display: flex;
        justify-content: space-between; align-items: center;
    }
    .brand-header h1 {
        margin: 0; font-size: 1.6rem; font-weight: 700; color: white !important;
    }
    .brand-header p {
        margin: 0.15rem 0 0 0; font-size: 0.85rem; opacity: 0.85; color: white !important;
    }
    .brand-contact {
        text-align: right; font-size: 0.8rem; color: white !important; line-height: 1.6;
    }
    .status-badge {
        display: inline-block; padding: 0.2rem 0.65rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin-right: 0.5rem;
    }
    .status-approved { background: #d4edda; color: #155724; }
    .category-header {
        font-size: 1.15rem; font-weight: 700; color: #40887d;
        border-bottom: 2px solid #40887d; padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }
    .cat-count {
        display: inline-block; background: #40887d; color: white;
        font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.55rem;
        border-radius: 12px; margin-left: 0.5rem; vertical-align: middle;
    }
    .vault-footer {
        text-align: center; font-size: 0.78rem; color: #999;
        border-top: 1px solid #e0e7e6; padding-top: 1.5rem; margin-top: 3rem;
    }
    section[data-testid="stSidebar"] { background: #f7faf9; }
    .sidebar-logo {
        font-size: 1.2rem; font-weight: 700; color: #40887d;
        text-align: center; padding: 0.75rem 0 0.25rem 0;
    }
    .sidebar-tagline {
        font-size: 0.78rem; color: #888; text-align: center; margin-bottom: 1.25rem;
    }
    .qrc-dot {
        display: inline-block; width: 12px; height: 12px; border-radius: 50%;
        margin-right: 0.4rem; vertical-align: middle;
    }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Authentication gate
# ---------------------------------------------------------------------------
user = require_auth()

# ---------------------------------------------------------------------------
# Supabase Storage helpers
# ---------------------------------------------------------------------------
BUCKET = "clinical-documents"
SIGNED_URL_EXPIRY = 3600  # 1 hour


def _storage_headers():
    """Return HTTP headers for authenticated Supabase Storage API calls."""
    from auth import _resolve_env
    url, key = _resolve_env()
    token = st.session_state.get("access_token", key)
    return url, {
        "apikey": key,
        "Authorization": f"Bearer {token}",
    }


def get_signed_url(file_path: str) -> str:
    """Generate a signed download URL via REST API."""
    url, headers = _storage_headers()
    resp = requests.post(
        f"{url}/storage/v1/object/sign/{BUCKET}/{file_path}",
        headers=headers,
        json={"expiresIn": SIGNED_URL_EXPIRY},
    )
    if resp.ok:
        signed_path = resp.json().get("signedURL", "")
        if signed_path:
            return f"{url}/storage/v1{signed_path}"
    return ""


def download_pdf_bytes(file_path: str) -> bytes | None:
    """Download a PDF's raw bytes from storage for inline display."""
    url, headers = _storage_headers()
    resp = requests.get(
        f"{url}/storage/v1/object/authenticated/{BUCKET}/{file_path}",
        headers=headers,
    )
    if resp.ok:
        return resp.content
    return None


def log_download(user_email: str, document_code: str, document_title: str):
    """Log a download event to the vault_downloads audit table."""
    client = _get_client()
    token = st.session_state.get("access_token", "")
    if token:
        client.postgrest.auth(token)
    try:
        client.table("vault_downloads").insert({
            "user_email": user_email,
            "document_code": document_code,
            "document_title": document_title,
        }).execute()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------
STORAGE_PATHS = {
    "MANUAL": "manual/NOH_Clinical_Operations_Manual_V1.0.pdf",
    "SOP-001": "sops/SOP-001_Controlled_Drugs_Management.pdf",
    "SOP-002": "sops/SOP-002_Major_Haemorrhage_Protocol.pdf",
    "SOP-003": "sops/SOP-003_Normal_Labour_and_Delivery.pdf",
    "SOP-004": "sops/SOP-004_Hypertensive_Disorders_in_Pregnancy.pdf",
    "SOP-005": "sops/SOP-005_Shoulder_Dystocia_Management.pdf",
    "SOP-006": "sops/SOP-006_Cord_Prolapse_Management.pdf",
    "SOP-007": "sops/SOP-007_Caesarean_Section_Pathway.pdf",
    "SOP-008": "sops/SOP-008_Neonatal_Resuscitation.pdf",
    "SOP-009": "sops/SOP-009_HIV_in_Pregnancy_PMTCT.pdf",
    "SOP-010": "sops/SOP-010_Referral_and_Inter-Facility_Transfer.pdf",
    "SOP-011": "sops/SOP-011_Blood_Transfusion_and_MTP.pdf",
    "QRC-001": "qrcs/QRC-001_PPH_Algorithm.pdf",
    "QRC-002": "qrcs/QRC-002_Eclampsia_Algorithm.pdf",
    "QRC-003": "qrcs/QRC-003_Partograph_Quick_Guide.pdf",
    "QRC-004": "qrcs/QRC-004_Shoulder_Dystocia_HELPERR.pdf",
    "QRC-005": "qrcs/QRC-005_Cord_Prolapse_Algorithm.pdf",
    "QRC-006": "qrcs/QRC-006_Emergency_CS_Checklist.pdf",
    "QRC-007": "qrcs/QRC-007_NLS_Algorithm.pdf",
    "QRC-009": "qrcs/QRC-009_PMTCT_Quick_Reference.pdf",
    "QRC-010": "qrcs/QRC-010_Transfer_Checklist.pdf",
    "QRC-011": "qrcs/QRC-011_Massive_Transfusion_Protocol.pdf",
}

# All documents in one flat list for the sidebar selector
ALL_DOCS = [
    {"code": "MANUAL", "title": "Clinical Operations Manual V1.0", "category": "Manual",
     "description": "Comprehensive clinical governance manual covering all aspects of maternity and obstetric care at Network One Health facilities.",
     "meta": "12 Chapters | 3 Appendices | 903 KB"},
    {"code": "SOP-001", "title": "Controlled Drugs Management", "category": "SOP", "area": "Medicines"},
    {"code": "SOP-002", "title": "Major Haemorrhage Protocol", "category": "SOP", "area": "Emergency"},
    {"code": "SOP-003", "title": "Normal Labour and Delivery", "category": "SOP", "area": "Intrapartum"},
    {"code": "SOP-004", "title": "Hypertensive Disorders in Pregnancy", "category": "SOP", "area": "Emergency"},
    {"code": "SOP-005", "title": "Shoulder Dystocia (HELPERR)", "category": "SOP", "area": "Emergency"},
    {"code": "SOP-006", "title": "Cord Prolapse", "category": "SOP", "area": "Emergency"},
    {"code": "SOP-007", "title": "Caesarean Section Pathway", "category": "SOP", "area": "Intrapartum"},
    {"code": "SOP-008", "title": "Neonatal Resuscitation (NLS)", "category": "SOP", "area": "Newborn"},
    {"code": "SOP-009", "title": "HIV in Pregnancy (PMTCT)", "category": "SOP", "area": "Antenatal"},
    {"code": "SOP-010", "title": "Referral and Inter-Facility Transfer", "category": "SOP", "area": "Operations"},
    {"code": "SOP-011", "title": "Blood Transfusion and MTP", "category": "SOP", "area": "Emergency"},
    {"code": "QRC-001", "title": "PPH Algorithm", "category": "QRC", "colour": "RED"},
    {"code": "QRC-002", "title": "Eclampsia Algorithm", "category": "QRC", "colour": "PURPLE"},
    {"code": "QRC-003", "title": "Partograph Quick Guide", "category": "QRC", "colour": "BLUE"},
    {"code": "QRC-004", "title": "Shoulder Dystocia (HELPERR)", "category": "QRC", "colour": "GREEN"},
    {"code": "QRC-005", "title": "Cord Prolapse Algorithm", "category": "QRC", "colour": "AMBER"},
    {"code": "QRC-006", "title": "Emergency CS Checklist", "category": "QRC", "colour": "DARK BLUE"},
    {"code": "QRC-007", "title": "NLS Algorithm", "category": "QRC", "colour": "BLUE"},
    {"code": "QRC-009", "title": "PMTCT Quick Reference", "category": "QRC", "colour": "ORANGE"},
    {"code": "QRC-010", "title": "Transfer Checklist", "category": "QRC", "colour": "TEAL"},
    {"code": "QRC-011", "title": "Massive Transfusion Protocol", "category": "QRC", "colour": "DARK RED"},
]

QRC_COLOURS = {
    "RED": "#dc3545", "PURPLE": "#6f42c1", "BLUE": "#0d6efd",
    "GREEN": "#198754", "AMBER": "#fd7e14", "DARK BLUE": "#0a3d62",
    "ORANGE": "#e67e22", "TEAL": "#40887d", "DARK RED": "#8b0000",
}

AREA_ICONS = {
    "Medicines": "\U0001f48a", "Emergency": "\U0001f6a8",
    "Intrapartum": "\U0001f476", "Newborn": "\U0001f90d",
    "Antenatal": "\U0001fa7a", "Operations": "\U0001f4cb",
}


# ---------------------------------------------------------------------------
# Sidebar — document selector
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-logo">NOH Clinical Vault</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Secure Document Repository</div>', unsafe_allow_html=True)
    st.divider()

    # Category filter
    category = st.radio(
        "Category",
        ["All Documents", "Manual", "SOPs", "Quick Reference Cards"],
        label_visibility="collapsed",
    )

    # Filter documents by category
    if category == "Manual":
        filtered_docs = [d for d in ALL_DOCS if d["category"] == "Manual"]
    elif category == "SOPs":
        filtered_docs = [d for d in ALL_DOCS if d["category"] == "SOP"]
    elif category == "Quick Reference Cards":
        filtered_docs = [d for d in ALL_DOCS if d["category"] == "QRC"]
    else:
        filtered_docs = ALL_DOCS

    st.divider()

    # Document selector
    doc_labels = [f"{d['code']} — {d['title']}" for d in filtered_docs]
    selected_label = st.radio("Select a document to view:", doc_labels, label_visibility="visible")

    # Find the selected document
    selected_idx = doc_labels.index(selected_label) if selected_label in doc_labels else 0
    selected_doc = filtered_docs[selected_idx]

    st.divider()
    user_email = getattr(user, "email", "Authenticated user")
    st.caption(f"Signed in as **{user_email}**")
    logout_button()
    st.divider()
    st.caption("Phone: 011 458 2497")
    st.caption("WhatsApp: 066 499 2713")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
HEADER_HTML = """
<div class="brand-header">
    <div>
        <h1>NOH Clinical Vault</h1>
        <p>Secure clinical governance document repository</p>
    </div>
    <div class="brand-contact">
        <strong>Network One Health</strong><br>
        Phone: 011 458 2497<br>
        WhatsApp: 066 499 2713
    </div>
</div>
"""
st.markdown(HEADER_HTML, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Document viewer
# ---------------------------------------------------------------------------
doc = selected_doc
code = doc["code"]
title = doc["title"]
file_path = STORAGE_PATHS.get(code, "")

# Document title bar
col_title, col_badge = st.columns([4, 1])
with col_title:
    if doc["category"] == "QRC":
        colour = doc.get("colour", "")
        hex_colour = QRC_COLOURS.get(colour, "#999")
        st.markdown(
            f'<span class="qrc-dot" style="background:{hex_colour};"></span> '
            f'**{code}** — {title}',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"**{code}** — {title}")
with col_badge:
    st.markdown(
        '<span class="status-badge status-approved">Approved</span>',
        unsafe_allow_html=True,
    )

# Show document metadata
if doc.get("description"):
    st.caption(doc["description"])
if doc.get("meta"):
    st.caption(doc["meta"])
if doc.get("area"):
    icon = AREA_ICONS.get(doc["area"], "")
    st.caption(f"{icon} {doc['area']}")

st.divider()

# Get a signed URL for this document (used for both viewing and open-in-new-tab)
signed_url = get_signed_url(file_path)

# Action buttons
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if signed_url:
        st.link_button("Open in New Tab", signed_url, use_container_width=True)
    else:
        st.button("Open in New Tab", disabled=True, key=f"view_{code}", use_container_width=True)

with col2:
    pdf_data = download_pdf_bytes(file_path)
    if pdf_data:
        filename = file_path.split("/")[-1]
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name=filename,
            mime="application/pdf",
            key=f"dl_{code}",
            use_container_width=True,
        )
    else:
        st.button("Download unavailable", disabled=True, key=f"dl_{code}", use_container_width=True)

# ---------------------------------------------------------------------------
# Inline PDF viewer — uses PDF.js to render on canvas (bypasses all iframe blocks)
# ---------------------------------------------------------------------------
st.markdown(
    f'<div class="category-header">{title}</div>',
    unsafe_allow_html=True,
)

if pdf_data:
    import base64
    import streamlit.components.v1 as components
    b64 = base64.b64encode(pdf_data).decode("utf-8")
    components.html(
        f"""
        <div id="pdf-controls" style="
            display:flex; align-items:center; gap:12px;
            padding:8px 12px; background:#f7faf9; border:1px solid #e0e7e6;
            border-radius:8px 8px 0 0; font-family:Arial,sans-serif; font-size:14px;">
            <button onclick="prevPage()" style="padding:4px 12px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:white;">Prev</button>
            <span>Page <span id="page-num">1</span> of <span id="page-count">-</span></span>
            <button onclick="nextPage()" style="padding:4px 12px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:white;">Next</button>
            <span style="margin-left:auto;color:#888;font-size:12px;">Zoom:</span>
            <button onclick="changeZoom(-0.25)" style="padding:4px 8px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:white;">-</button>
            <button onclick="changeZoom(0.25)" style="padding:4px 8px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:white;">+</button>
        </div>
        <div id="pdf-container" style="
            border:1px solid #e0e7e6; border-top:none; border-radius:0 0 8px 8px;
            overflow-y:auto; height:750px; background:#525659; text-align:center;">
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

            var pdfData = atob("{b64}");
            var pdfDoc = null;
            var currentPage = 1;
            var currentScale = 1.5;

            function renderAllPages() {{
                var container = document.getElementById('pdf-container');
                container.innerHTML = '';
                for (var i = 1; i <= pdfDoc.numPages; i++) {{
                    renderPage(i, container);
                }}
            }}

            function renderPage(num, container) {{
                pdfDoc.getPage(num).then(function(page) {{
                    var scale = currentScale;
                    var viewport = page.getViewport({{ scale: scale }});
                    var canvas = document.createElement('canvas');
                    canvas.style.display = 'block';
                    canvas.style.margin = '10px auto';
                    canvas.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    container.appendChild(canvas);

                    var ctx = canvas.getContext('2d');
                    page.render({{ canvasContext: ctx, viewport: viewport }});
                }});
            }}

            function prevPage() {{
                if (currentPage <= 1) return;
                currentPage--;
                renderSinglePage(currentPage);
            }}

            function nextPage() {{
                if (currentPage >= pdfDoc.numPages) return;
                currentPage++;
                renderSinglePage(currentPage);
            }}

            function renderSinglePage(num) {{
                document.getElementById('page-num').textContent = num;
                var container = document.getElementById('pdf-container');
                container.innerHTML = '';
                pdfDoc.getPage(num).then(function(page) {{
                    var viewport = page.getViewport({{ scale: currentScale }});
                    var canvas = document.createElement('canvas');
                    canvas.style.display = 'block';
                    canvas.style.margin = '10px auto';
                    canvas.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    container.appendChild(canvas);
                    var ctx = canvas.getContext('2d');
                    page.render({{ canvasContext: ctx, viewport: viewport }});
                }});
            }}

            function changeZoom(delta) {{
                currentScale = Math.max(0.5, Math.min(3.0, currentScale + delta));
                renderSinglePage(currentPage);
            }}

            var loadingTask = pdfjsLib.getDocument({{ data: pdfData }});
            loadingTask.promise.then(function(pdf) {{
                pdfDoc = pdf;
                document.getElementById('page-count').textContent = pdf.numPages;
                renderSinglePage(1);
            }});
        </script>
        """,
        height=820,
        scrolling=False,
    )
    log_download(user_email, code, title)
else:
    st.warning("PDF could not be loaded. Check storage permissions.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
FOOTER_HTML = """
<div class="vault-footer">
    Network One Health &nbsp;|&nbsp; Clinical Vault &nbsp;|&nbsp;
    For authorised healthcare professionals only
</div>
"""
st.markdown(FOOTER_HTML, unsafe_allow_html=True)
