"""
NOH Clinical Vault
Secure document repository for Network One Health clinical governance documents.
Includes the Clinical Operations Manual, 11 SOPs, and 10 QRCs.
"""

import streamlit as st
from auth import require_auth, logout_button

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
    .doc-card {
        background: #ffffff; border: 1px solid #e0e7e6; border-radius: 10px;
        padding: 1.1rem 1.25rem; margin-bottom: 0.75rem;
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .doc-card:hover {
        box-shadow: 0 4px 16px rgba(64, 136, 125, 0.12); border-color: #40887d;
    }
    .doc-code { font-weight: 700; font-size: 0.95rem; color: #40887d; margin-bottom: 0.15rem; }
    .doc-title { font-size: 1rem; font-weight: 600; color: #1a1a1a; margin-bottom: 0.35rem; }
    .doc-meta { font-size: 0.8rem; color: #666; }
    .status-badge {
        display: inline-block; padding: 0.2rem 0.65rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin-right: 0.5rem;
    }
    .status-review { background: #fff3cd; color: #856404; }
    .status-approved { background: #d4edda; color: #155724; }
    .qrc-dot {
        display: inline-block; width: 12px; height: 12px; border-radius: 50%;
        margin-right: 0.4rem; vertical-align: middle;
    }
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
    .manual-card {
        background: linear-gradient(135deg, #f0f9f7 0%, #e8f4f1 100%);
        border: 2px solid #40887d; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
    }
    .manual-card h3 { color: #40887d; margin: 0 0 0.5rem 0; font-size: 1.15rem; }
    .manual-stat {
        display: inline-block; background: white; padding: 0.4rem 0.8rem;
        border-radius: 8px; font-size: 0.82rem; margin: 0.25rem 0.25rem 0.25rem 0;
        border: 1px solid #d0e0dd;
    }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Authentication gate
# ---------------------------------------------------------------------------
user = require_auth()

# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------
SOPS = [
    {"code": "SOP-001", "title": "Controlled Drugs Management", "area": "Medicines", "status": "Awaiting CMO Review"},
    {"code": "SOP-002", "title": "Major Haemorrhage Protocol", "area": "Emergency", "status": "Awaiting CMO Review"},
    {"code": "SOP-003", "title": "Normal Labour and Delivery", "area": "Intrapartum", "status": "Awaiting CMO Review"},
    {"code": "SOP-004", "title": "Hypertensive Disorders", "area": "Emergency", "status": "Awaiting CMO Review"},
    {"code": "SOP-005", "title": "Shoulder Dystocia (HELPERR)", "area": "Emergency", "status": "Awaiting CMO Review"},
    {"code": "SOP-006", "title": "Cord Prolapse", "area": "Emergency", "status": "Awaiting CMO Review"},
    {"code": "SOP-007", "title": "Caesarean Section Pathway", "area": "Intrapartum", "status": "Awaiting CMO Review"},
    {"code": "SOP-008", "title": "Neonatal Resuscitation (NLS)", "area": "Newborn", "status": "Awaiting CMO Review"},
    {"code": "SOP-009", "title": "HIV in Pregnancy (PMTCT)", "area": "Antenatal", "status": "Awaiting CMO Review"},
    {"code": "SOP-010", "title": "Referral and Inter-Facility Transfer", "area": "Operations", "status": "Awaiting CMO Review"},
    {"code": "SOP-011", "title": "Blood Transfusion and MTP", "area": "Emergency", "status": "Awaiting CMO Review"},
]

QRC_COLOURS = {
    "RED": "#dc3545", "PURPLE": "#6f42c1", "BLUE": "#0d6efd",
    "GREEN": "#198754", "AMBER": "#fd7e14", "DARK BLUE": "#0a3d62",
    "ORANGE": "#e67e22", "TEAL": "#40887d", "DARK RED": "#8b0000",
}

QRCS = [
    {"code": "QRC-001", "title": "PPH Algorithm", "colour": "RED", "status": "Awaiting CMO Review"},
    {"code": "QRC-002", "title": "Eclampsia", "colour": "PURPLE", "status": "Awaiting CMO Review"},
    {"code": "QRC-003", "title": "Partograph Guide", "colour": "BLUE", "status": "Awaiting CMO Review"},
    {"code": "QRC-004", "title": "Shoulder Dystocia (HELPERR)", "colour": "GREEN", "status": "Awaiting CMO Review"},
    {"code": "QRC-005", "title": "Cord Prolapse", "colour": "AMBER", "status": "Awaiting CMO Review"},
    {"code": "QRC-006", "title": "Emergency CS Checklist", "colour": "DARK BLUE", "status": "Awaiting CMO Review"},
    {"code": "QRC-007", "title": "NLS Algorithm", "colour": "BLUE", "status": "Awaiting CMO Review"},
    {"code": "QRC-009", "title": "PMTCT Quick Reference", "colour": "ORANGE", "status": "Awaiting CMO Review"},
    {"code": "QRC-010", "title": "Transfer Checklist", "colour": "TEAL", "status": "Awaiting CMO Review"},
    {"code": "QRC-011", "title": "MTP", "colour": "DARK RED", "status": "Awaiting CMO Review"},
]

MANUAL_CHAPTERS = [
    "1. Governance and Accountability",
    "2. Clinical Standards and Quality",
    "3. Patient Safety",
    "4. Antenatal Care",
    "5. Intrapartum Care",
    "6. Postnatal Care",
    "7. Newborn Care",
    "8. Obstetric Emergencies",
    "9. Medicines Management",
    "10. Infection Prevention and Control",
    "11. Training and Competency",
    "12. Business Continuity and Major Incident",
]

MANUAL_APPENDICES = [
    "Appendix A: Document Register",
    "Appendix B: Abbreviations and Definitions",
    "Appendix C: Audit Tools",
]

AREA_ICONS = {
    "Medicines": "\U0001f48a",
    "Emergency": "\U0001f6a8",
    "Intrapartum": "\U0001f476",
    "Newborn": "\U0001f90d",
    "Antenatal": "\U0001fa7a",
    "Operations": "\U0001f4cb",
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">NOH Clinical Vault</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-tagline">Secure Document Repository</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    view = st.radio(
        "Document Category",
        [
            "Clinical Operations Manual",
            "Standard Operating Procedures (11)",
            "Quick Reference Cards (10)",
        ],
        index=0,
        label_visibility="collapsed",
    )

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


def status_html(status: str) -> str:
    """Return an HTML badge for a document status."""
    css_class = "status-approved" if status == "Approved" else "status-review"
    return f'<span class="status-badge {css_class}">{status}</span>'


# ---------------------------------------------------------------------------
# View: Clinical Operations Manual
# ---------------------------------------------------------------------------
if view == "Clinical Operations Manual":
    st.markdown(
        '<div class="category-header">Clinical Operations Manual</div>',
        unsafe_allow_html=True,
    )

    badge = status_html("Awaiting CMO Review")
    manual_html = f"""
    <div class="manual-card">
        <h3>NOH Clinical Operations Manual V1.0</h3>
        <p style="margin:0 0 0.75rem 0; font-size:0.9rem; color:#444;">
            Comprehensive clinical governance manual covering all aspects of
            maternity and obstetric care at Network One Health facilities.
        </p>
        <div>
            <span class="manual-stat"><strong>12</strong> Chapters</span>
            <span class="manual-stat"><strong>3</strong> Appendices</span>
            <span class="manual-stat"><strong>903 KB</strong></span>
            <span class="manual-stat">{badge}</span>
        </div>
    </div>
    """
    st.markdown(manual_html, unsafe_allow_html=True)

    st.markdown("##### Chapters")
    cols = st.columns(2)
    for i, ch in enumerate(MANUAL_CHAPTERS):
        with cols[i % 2]:
            st.markdown(
                f'<div class="doc-card"><div class="doc-title">{ch}</div>'
                f'<div class="doc-meta">Complete</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("##### Appendices")
    cols = st.columns(3)
    for i, app_name in enumerate(MANUAL_APPENDICES):
        with cols[i]:
            st.markdown(
                f'<div class="doc-card"><div class="doc-title">{app_name}</div>'
                f'<div class="doc-meta">Complete</div></div>',
                unsafe_allow_html=True,
            )

    st.button(
        "PDF pending CMO approval",
        disabled=True,
        use_container_width=True,
        key="manual_download",
    )


# ---------------------------------------------------------------------------
# View: Standard Operating Procedures
# ---------------------------------------------------------------------------
elif view == "Standard Operating Procedures (11)":
    st.markdown(
        '<div class="category-header">Standard Operating Procedures'
        '<span class="cat-count">11</span></div>',
        unsafe_allow_html=True,
    )

    areas = sorted(set(s["area"] for s in SOPS))
    selected_area = st.selectbox("Filter by clinical area", ["All"] + areas)
    filtered = SOPS if selected_area == "All" else [s for s in SOPS if s["area"] == selected_area]

    for sop in filtered:
        icon = AREA_ICONS.get(sop["area"], "")
        badge = status_html(sop["status"])
        sop_html = f"""
        <div class="doc-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="doc-code">{sop["code"]}</div>
                    <div class="doc-title">{sop["title"]}</div>
                    <div class="doc-meta">{icon} {sop["area"]}</div>
                </div>
                <div style="text-align:right;">{badge}</div>
            </div>
        </div>
        """
        st.markdown(sop_html, unsafe_allow_html=True)
        st.button(
            "PDF pending CMO approval",
            disabled=True,
            key=f"dl_{sop['code']}",
        )


# ---------------------------------------------------------------------------
# View: Quick Reference Cards
# ---------------------------------------------------------------------------
elif view == "Quick Reference Cards (10)":
    st.markdown(
        '<div class="category-header">Quick Reference Cards'
        '<span class="cat-count">10</span></div>',
        unsafe_allow_html=True,
    )

    for qrc in QRCS:
        hex_colour = QRC_COLOURS.get(qrc["colour"], "#999999")
        badge = status_html(qrc["status"])
        qrc_html = f"""
        <div class="doc-card" style="border-left: 4px solid {hex_colour};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="doc-code">{qrc["code"]}</div>
                    <div class="doc-title">
                        <span class="qrc-dot" style="background:{hex_colour};"></span>
                        {qrc["title"]}
                    </div>
                    <div class="doc-meta">Colour code: {qrc["colour"]}</div>
                </div>
                <div style="text-align:right;">{badge}</div>
            </div>
        </div>
        """
        st.markdown(qrc_html, unsafe_allow_html=True)
        st.button(
            "PDF pending CMO approval",
            disabled=True,
            key=f"dl_{qrc['code']}",
        )


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
