import os
import time
from datetime import datetime
import streamlit as st
from dholera_port.config.database import DatabaseConfig

class PaymentProcessor:
    """Handles payment simulation and receipt generation."""
    
    # Port Authority Bank Details
    BANK_DETAILS = {
        "bank_name": os.getenv("PORT_BANK_NAME", "State Bank of India"),
        "account_name": os.getenv("PORT_ACCOUNT_NAME", "Dholera Smart Port Authority"),
        "account_number": os.getenv("PORT_BANK_ACCOUNT", "DHOLERA001234567"),
        "ifsc_code": os.getenv("PORT_IFSC_CODE", "SBIN000101"),
        "swift_code": os.getenv("PORT_SWIFT_CODE", "SBININBB104"),
        "branch": os.getenv("PORT_BRANCH", "Dholera Port Branch"),
        "address": "Dholera Special Investment Region, Gujarat, India",
        "gstin": os.getenv("PORT_GSTIN", "24AABCU9603R1ZX"),
        "pan": os.getenv("PORT_PAN", "AABCU9603R")
    }
    
    PAYMENT_METHODS = {
        "RTGS": {
            "name": "RTGS (Real Time Gross Settlement)",
            "processing_time": "Immediate",
            "min_amount": 200000,
            "charges": 0,
            "description": "Real-time transfer for high-value transactions"
        },
        "SWIFT": {
            "name": "SWIFT (Society for Worldwide Interbank Financial Telecommunication)",
            "processing_time": "1-2 business days",
            "min_amount": 0,
            "charges": 500,
            "description": "International wire transfer"
        }
    }
    
    @staticmethod
    def simulate_payment_processing(amount, payment_method):
        """Simulates a quick payment process using a Streamlit progress bar."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = [
            ("Connecting to Payment Gateway...", 0.2),
            ("Validating Transaction Details...", 0.4),
            ("Authenticating with Bank...", 0.6),
            ("Processing Payment...", 0.8),
            ("Transaction Approved", 1.0)
        ]
        
        for step_text, progress in steps:
            status_text.text(step_text)
            progress_bar.progress(progress)
            # time.sleep(0.6) # Removed for faster processing
        
        progress_bar.empty()
        status_text.empty()
    
    @staticmethod
    def generate_receipt(ref_no, payment_type, amount, payment_method, user_details, transaction_details=None):
        """Generate industry-standard receipt with all details"""
        receipt = {
            "receipt_number": ref_no,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "payment_type": payment_type,
            "amount": amount,
            "payment_method": payment_method,
            "user": user_details,
            "bank_details": PaymentProcessor.BANK_DETAILS,
            "transaction_details": transaction_details or {},
            "gst_details": {
                "gstin": PaymentProcessor.BANK_DETAILS["gstin"],
                "cgst": round(amount * 0.09, 2) if amount > 0 else 0,
                "sgst": round(amount * 0.09, 2) if amount > 0 else 0,
                "igst": round(amount * 0.18, 2) if amount > 0 else 0,
                "total_gst": round(amount * 0.18, 2) if amount > 0 else 0
            }
        }
        return receipt
    
    @staticmethod
    def display_sophisticated_success():
        """Display sophisticated success animation instead of balloons"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; color: #4CAF50; animation: pulse 2s infinite;">
                ✓
            </div>
            <div style="font-size: 1.5rem; color: #4CAF50; margin-top: 1rem; font-weight: bold;">
                Transaction Successful
            </div>
            <div style="color: #666; margin-top: 0.5rem;">
                Payment processed and confirmed
            </div>
        </div>
        <style>
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        </style>
        """, unsafe_allow_html=True)
        time.sleep(1.5)
        st.markdown("""
        <script>
        setTimeout(function() {
            document.querySelector('[style*="animation: pulse"]').style.animation = 'none';
        }, 2000);
        </script>
        """, unsafe_allow_html=True)

def record_payment(ref_no, related_id, p_type, amount, username, payment_method="RTGS"):
    query = "INSERT INTO payments (ref_no, related_id, payment_type, amount, username, timestamp) VALUES (%s, %s, %s, %s, %s, %s)"
    params = (ref_no, related_id, f"{p_type} ({payment_method})", amount, username, datetime.now())
    DatabaseConfig.execute_query(query, params)
