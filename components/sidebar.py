"""
RR TalentIQ - Clean Sidebar Navigation Component
Renders compact branded navigation, scout badge, platform metrics, and session controls.
"""

import streamlit as st
from auth.authentication import is_authenticated, login_session, logout_session

def render_sidebar():
    """Renders the navigation sidebar with scout badge, quick metrics, and logout control."""
    with st.sidebar:
        # Platform Logo / Title
        st.markdown("""
        <div style="text-align: center; padding: 0.2rem 0 0.8rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.8rem;">
            <div style="font-size: 2rem; margin-bottom: 0.2rem;">👑</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">RR <span style="color: #ff2a85;">TALENT</span><span style="color: #00b4d8;">IQ</span></div>
            <div style="font-size: 0.7rem; color: #ff75a0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">SupeRR Selector Season 2</div>
            <div style="font-size: 0.66rem; color: #94a3b8; margin-top: 0.15rem;">IPL 2027 Auction Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        # User Authentication Status
        if is_authenticated():
            user = st.session_state.get("user", {}) or {}
            username = user.get("username", "RR Scout")
            role = user.get("role", "analyst").upper()
            
            st.markdown(f"""
            <div style="background: rgba(28, 37, 65, 0.7); border: 1px solid rgba(255, 42, 133, 0.3); border-radius: 8px; padding: 0.65rem 0.8rem; margin-bottom: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #ffffff;">👤 {username.title()}</div>
                        <div style="font-size: 0.7rem; color: #94a3b8;">Role: <span style="color: #48cae4; font-weight: 600;">{role}</span></div>
                    </div>
                    <div style="background: #27ae60; width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 6px #27ae60;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Log Out", use_container_width=True):
                logout_session()
                st.rerun()
        else:
            st.info("🔒 Guest Scout Mode.")
            if st.button("⚡ Sign In as RR Scout", use_container_width=True):
                login_session({
                    "id": 1,
                    "username": "RR Scout",
                    "email": "scout@rajasthanroyals.com",
                    "role": "analyst"
                })
                st.rerun()
                
        st.divider()
        
        # RR Competition Intelligence Badges
        st.markdown("""
        <div style="font-size: 0.72rem; color: #94a3b8; line-height: 1.6;">
            <div style="margin-bottom: 0.3rem;"><b style="color: #ffffff;">Target:</b> IPL 2027 Auction</div>
            <div style="margin-bottom: 0.3rem;"><b style="color: #ffffff;">Eligibility:</b> Young Uncapped Talent</div>
            <div style="margin-bottom: 0.3rem;"><b style="color: #ffffff;">Metrics:</b> 36 Normalized Metrics</div>
            <div style="margin-bottom: 0.3rem;"><b style="color: #ffffff;">Historical:</b> 1,243 Matches (2008–2026)</div>
            <div><b style="color: #ffffff;">Status:</b> Round 1 Strategy Active</div>
        </div>
        """, unsafe_allow_html=True)
