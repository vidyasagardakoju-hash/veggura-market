import streamlit as st
import pandas as pd
import urllib.parse
import os

# --- 1. DATA CONNECTION ---
SHEET_ID = "1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6"
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-{SHEET_ID}/pub?output=csv"

def load_data():
    try:
        # The timestamp forces the app to refresh data every time you reload
        df = pd.read_csv(f"{CSV_URL}&t={pd.Timestamp.now().timestamp()}")
        df.columns = df.columns.str.strip()
        # Clean up text to prevent "Hidden Space" glitches
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].str.strip()
        return df
    except Exception as e:
        st.error(f"Data Glitch: {e}")
        return None

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")
st.info("Fresh vegetables delivered to your doorstep!")

# --- 3. DISPLAY PRODUCTS ---
df = load_data()

if df is not None:
    # We define exactly which categories we want to show
    target_categories = ["Leafy Vegetables", "Root Vegetables", "General Vegetables"]
    
    for cat in target_categories:
        cat_df = df[df['category'] == cat]
        
        if not cat_df.empty:
            st.markdown(f"## 🛒 {cat}")
            
            # This creates the 3-column grid per category
            cols = st.columns(3)
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    name = row['name']
                    price = row['price']
                    unit = row['unit']
                    available = str(row['is_available']).upper() == "TRUE"
                    
                    # --- IMAGE LOGIC ---
                    # It looks for 'tomato.jpg' (lowercase, no spaces)
                    img_file = f"{name.lower().replace(' ', '_')}.jpg"
                    
                    if available:
                        try:
                            # Try to load the image from your GitHub folder
                            st.image(img_file, use_container_width=True)
                        except:
                            st.warning(f"📷 Photo coming soon for {name}")
                        
                        st.subheader(name)
                        st.write(f"**Price:** ₹{price} / {unit}")
                        
                        qty = st.number_input(f"Amount", min_value=0.0, step=0.5, key=f"q_{name}")
                        if st.button(f"Add {name}", key=f"b_{name}"):
                            if qty > 0:
                                st.session_state.cart[name] = {"qty": qty, "total": qty * price, "unit": unit}
                                st.toast(f"✅ Added {name}")
                    else:
                        st.write(f"### ~~{name}~~")
                        st.error("Out of Stock")
            st.markdown("---")

# --- 4. SIDEBAR ---
st.sidebar.header("📋 Your Order")
if st.session_state.cart:
    total = 0
    order_text = "Hello Veggura! I want to order:\n\n"
    for item, d in st.session_state.cart.items():
        line = f"• {item}: {d['qty']} {d['unit']} (₹{d['total']})\n"
        st.sidebar.write(line)
        order_text += line
        total += d['total']
    
    st.sidebar.subheader(f"Total Bill: ₹{total}")
    
    # Change this to your 10-digit mobile number
    MY_NUMBER = "919948807525" 
    
    msg = urllib.parse.quote(order_text + f"\n*Grand Total: ₹{total}*")
    st.sidebar.link_button("🚀 Order via WhatsApp", f"https://wa.me/{MY_NUMBER}?text={msg}", use_container_width=True)
    
    if st.sidebar.button("Clear Cart"):
        st.session_state.cart = {}
        st.rerun()
