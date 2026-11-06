"""
IPL Analytics Pro - Sidebar Component
Renders branded navigation sidebar, active session details, and platform controls.
"""

import streamlit as st
from auth.authentication import is_authenticated, logout_session

def render_sidebar():
    """Renders the navigation sidebar with user badge, quick metrics, and logout control."""
    with st.sidebar:
        # Platform Logo / Title
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1.2rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.2rem;">👑</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">RR <span style="color: #ff2a85;">TALENT</span><span style="color: #00b4d8;">IQ</span></div>
            <div style="font-size: 0.72rem; color: #ff75a0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">SupeRR Selector Season 2</div>
            <div style="font-size: 0.68rem; color: #94a3b8; margin-top: 0.2rem;">IPL 2027 Auction Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        
        # User Authentication Status
        if is_authenticated():
            user = st.session_state.get("user", {})
            username = user.get("username", "Analyst")
            role = user.get("role", "analyst").upper()
            
            st.markdown(f"""
            <div style="background: rgba(28, 37, 65, 0.7); border: 1px solid rgba(255, 183, 3, 0.3); border-radius: 8px; padding: 0.75rem; margin-bottom: 1.2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #ffffff;">👤 {username.title()}</div>
                        <div style="font-size: 0.7rem; color: #94a3b8;">Role: <span style="color: #48cae4; font-weight: 600;">{role}</span></div>
                    </div>
                    <div style="background: #27ae60; width: 8px; height: 8px; border-radius: 50%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Log Out", use_container_width=True):
                logout_session()
                st.rerun()
        else:
            st.info("🔒 Guest Mode. Sign in for complete analyst access.")
            if st.button("🔑 Sign In / Register", use_container_width=True):
                st.switch_page("app.py")
                
        st.divider()
        
        # Dataset Overview Badges
        st.markdown("""
        <div style="font-size: 0.75rem; color: #94a3b8; line-height: 1.6;">
            <div style="margin-bottom: 0.4rem;"><b>Data Source:</b> Cricsheet Official</div>
            <div style="margin-bottom: 0.4rem;"><b>Total Matches:</b> 1,243 Verified</div>
            <div style="margin-bottom: 0.4rem;"><b>Total Deliveries:</b> 295,732</div>
            <div style="margin-bottom: 0.4rem;"><b>Coverage:</b> 2008 – 2026 (19 Seasons)</div>
            <div><b>Last Verified:</b> October 2026</div>
        </div>
        """, unsafe_allow_html=True)
