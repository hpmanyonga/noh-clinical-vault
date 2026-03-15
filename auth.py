"""
auth.py - Supabase authentication for NOH apps
Stores refresh token in browser query params to persist sessions across refreshes.
Session lasts until Supabase refresh token expires (default 7 days, configurable in dashboard).
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


def _try_restore_session():
    """Try to restore session from refresh token stored in query params."""
    params = st.query_params
    rt = params.get("rt")
    if not rt:
        return None

    try:
        client = _get_client()
        response = client.auth.refresh_session(rt)
        if response and response.user:
            st.session_state["user"] = response.user
            st.session_state["access_token"] = response.session.access_token
            st.session_state["refresh_token"] = response.session.refresh_token
            # Update query param with new refresh token
            st.query_params["rt"] = response.session.refresh_token
            return response.user
    except Exception:
        # Refresh token expired or invalid — clear it
        if "rt" in st.query_params:
            del st.query_params["rt"]
    return None


def login_page():
    """Render the login page with NOH branding."""
    st.markdown(
        """
        <style>
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
            <div class="login-subtitle">Authorised access only</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_auth():
    """
    Enforce Supabase email/password authentication.
    Persists session via refresh token in URL query params.
    Returns the authenticated user or stops the app.
    """
    # 1. Already authenticated this session
    if "user" in st.session_state and st.session_state["user"] is not None:
        return st.session_state["user"]

    # 2. Try to restore from refresh token in query params
    restored_user = _try_restore_session()
    if restored_user:
        return restored_user

    # 3. Show login form
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
                    st.session_state["refresh_token"] = response.session.refresh_token
                    # Store refresh token in URL query params for persistence
                    st.query_params["rt"] = response.session.refresh_token
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
        for key in ["user", "access_token", "refresh_token"]:
            st.session_state.pop(key, None)
        # Clear the refresh token from URL
        if "rt" in st.query_params:
            del st.query_params["rt"]
        st.rerun()
