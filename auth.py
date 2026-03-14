"""
auth.py - Supabase authentication for NOH Clinical Vault
Pattern consistent with all NOH Streamlit apps.
"""

import streamlit as st
from supabase import create_client, Client


def _resolve_env():
    """Resolve Supabase credentials: st.secrets first, os.getenv fallback."""
    import os

    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
    return url, key


def _get_client() -> Client:
    """Return a cached Supabase client."""
    url, key = _resolve_env()
    if not url or not key:
        st.error("Supabase credentials not configured.")
        st.stop()
    return create_client(url, key)


def login_page():
    """Render the login page with NOH Clinical Vault branding."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            .login-container {
                max-width: 420px;
                margin: 2rem auto;
                padding: 2.5rem 2rem;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                border-top: 4px solid #40887d;
            }
            .login-title {
                font-family: Arial, sans-serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: #40887d;
                text-align: center;
                margin-bottom: 0.25rem;
            }
            .login-subtitle {
                font-family: Arial, sans-serif;
                font-size: 0.95rem;
                color: #666666;
                text-align: center;
                margin-bottom: 1.5rem;
            }
            .login-warning {
                font-family: Arial, sans-serif;
                font-size: 0.8rem;
                color: #cc0000;
                text-align: center;
                margin-top: 1rem;
                padding: 0.5rem;
                background: #fff5f5;
                border-radius: 6px;
            }
        </style>
        <div class="login-container">
            <div class="login-title">Network One Health</div>
            <div class="login-subtitle">Clinical Vault &mdash; Authorised access only</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_auth():
    """
    Enforce Supabase email/password authentication.
    Returns the authenticated user dict or stops the app.
    """
    if "user" in st.session_state and st.session_state["user"] is not None:
        return st.session_state["user"]

    login_page()

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.warning("Please enter both email and password.")
                    st.stop()
                try:
                    client = _get_client()
                    response = client.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    st.session_state["user"] = response.user
                    st.session_state["access_token"] = response.session.access_token
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
                    st.stop()

            st.markdown(
                """
                <div class="login-warning">
                    This system contains confidential clinical documents.<br>
                    Unauthorised access is prohibited.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.stop()


def logout_button():
    """Render a logout button in the sidebar."""
    if st.sidebar.button("Sign Out", use_container_width=True):
        for key in ["user", "access_token"]:
            st.session_state.pop(key, None)
        st.rerun()
