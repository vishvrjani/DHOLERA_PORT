import os
import sys

# Add parent directory to path to allow imports from dholera_port package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import time
from dholera_port.config.database import DatabaseConfig
from dholera_port.utils.audit import log_audit
from dholera_port.utils.session import refresh_user_data
from dholera_port.ui.pages.auth import show_login_register
from dholera_port.ui.pages.ship_owner import show_ship_owner_menu
from dholera_port.ui.pages.cargo_owner import show_cargo_owner_menu
from dholera_port.ui.pages.trader import show_trader_menu
from dholera_port.ui.pages.admin import show_admin_menu
from dholera_port.ui.components.receipt import handle_receipt_display

# --- Main App Configuration ---
st.set_page_config(
    page_title="Dholera Smart Port",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-box:hover {
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Increase Global Font Size */
    html, body, [class*="css"] {
        font-size: 18px !important; 
    }
    .stMarkdown, .stText, p, div, label, .stButton button {
        font-size: 18px !important;
    }
    h1 { font-size: 32px !important; }
    h2 { font-size: 28px !important; }
    h3 { font-size: 24px !important; }
    .stSelectbox label { font-size: 20px !important; }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize Database
    DatabaseConfig.create_database_if_not_exists()
    DatabaseConfig.initialize_pool()
    DatabaseConfig.initialize_schema()
    
    # Session State Initialization
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'payment_in_progress' not in st.session_state:
        st.session_state.payment_in_progress = False

    handle_receipt_display()

    # Authentication Check
    if not st.session_state.current_user:
        show_login_register()
    else:
        user = st.session_state.current_user
        role = user['role']
        
        # Sidebar
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/2942/2942544.png", width=80)
            st.title("Dholera Port")
            st.write(f"Logged in as: **{user['name']}**")
            st.write(f"Role: **{role.replace('_', ' ').title()}**")
            
            if st.button("Logout", key="logout_btn"):
                log_audit(user['username'], 'LOGOUT', 'User logged in')
                st.session_state.current_user = None
                st.rerun()
            
            st.markdown("---")
            st.caption("© 2025 Dholera Port Authority")

        # Refresh user data periodically or on load
        refresh_user_data()

        # Route to specific dashboard
        if role == 'ship_owner':
            show_ship_owner_menu()
        elif role == 'cargo_owner':
            show_cargo_owner_menu()
        elif role == 'trader':
            show_trader_menu()
        elif role == 'admin':
            show_admin_menu()
        else:
            st.error("Unknown user role. Please contact support.")

if __name__ == "__main__":
    main()
