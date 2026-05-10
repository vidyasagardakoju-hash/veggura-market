import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. DATA CONNECTION ---
# Your confirmed Sheet ID
SHEET_ID = "1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6"
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-{SHEET_ID}/pub?output=csv"

def load_data():
    try:
        # The timestamp 't' forces the app to refresh data every time
        df = pd.read_csv(f"{CSV_URL}&t={pd.Timestamp.now().timestamp()}")
        # Clean up column names and text data
        df.columns = df.columns.str.strip()
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return None

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")
st.markdown("---")

# --- 3. DISPLAY PRODUCTS ---
df = load_data()

if df is not None:
    # This keeps your original 3-section layout
    target_categories = ["Leafy Vegetables", "Root Vegetables", "General Vegetables"]
    
    for cat in target_categories:
        cat_df = df[df['category'] == cat]
        
        if not cat_df.empty:
            st.header(f"🛒 {cat}")
            
            # Creates the 3-column grid for the products
            cols = st.columns(3)
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    name = row['name']
                    price = row['price']
                    unit = row['unit']
                    available = str(row['is_available']).upper() == "TRUE"
                    
                    if not available:
                        st.write(f"### ~~{name}~~")
                        st.error("Out of Stock")
                    else:
                       # --- SUPER SMART IMAGE LOGIC ---
                       # This version tries BOTH: 'black_brinjals.jpg' AND 'black brinjals.jpg'
                        clean_name = name.lower().strip()
                        underscore_name = clean_name.replace(' ', '_')

                        # List of possible names the computer might find
                        possible_files = [f"{underscore_name}.jpg", f"{clean_name}.jpg"]

                        image_found = False
                        for img_file in possible_files:
                            if not image_found:
                                try:
                                    st.image(img_file, use_container_width=True)
                                    image_found = True
                                except:
                                    continue

                        if not image_found:
                            st.caption(f"📷 Image matching '{underscore_name}.jpg' not found")
                            
                        st.write(f"### {name}")
                        st.info(f"₹{price} / {unit}")
                        
                        qty = st.number_input(f"Amount", min_value=0.0, step=0.5, key=f"q_{name}")
                        if st.button(f"Add {name}", key=f"b_{name}"):
                            if qty > 0:
                                st.session_state.cart[name] = {"qty": qty, "total": qty * price, "unit": unit}
                                st.toast(f"✅ Added {name}")
            st.markdown("---")

# --- 4. SIDEBAR & WHATSAPP ORDERING ---
st.sidebar.header("📋 Your Order Summary")

if st.session_state.cart:
    total_bill = 0
    order_msg = "Hello Veggura! I want to place an order:\n\n"
    
    for item, d in st.session_state.cart.items():
        line = f"• {item}: {d['qty']} {d['unit']} - ₹{d['total']}\n"
        st.sidebar.write(line)
        order_msg += line
        total_bill += d['total']
    
    st.sidebar.subheader(f"Total: ₹{total_bill}")
    
    # --- UPDATE YOUR NUMBER HERE ---
    # Put your 10-digit number after 91
    MY_NUMBER = "91XXXXXXXXXX" 
    
    final_msg = urllib.parse.quote(order_msg + f"\n*Grand Total: ₹{total_bill}*")
    wa_url = f"https://wa.me/{MY_NUMBER}?text={final_msg}"
    
    st.sidebar.link_button("🚀 Send Order to WhatsApp", wa_url, use_container_width=True)
    
    if st.sidebar.button("Clear Cart"):
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.write("Your cart is empty.")

st.sidebar.markdown("---")
st.sidebar.caption("Dakoju Vasantha Vidya Sagar")
