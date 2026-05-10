import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. DATA CONNECTION ---
SHEET_ID = "1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6"
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-{SHEET_ID}/pub?output=csv"

def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&t={pd.Timestamp.now().timestamp()}")
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

# --- CUSTOM CSS FOR PERFECT ALIGNMENT ---
st.markdown("""
    <style>
    /* This forces all images to be exactly 200px tall and fills the width */
    [data-testid="stImage"] img {
        height: 200px;
        object-fit: cover;
        border-radius: 5px;
    }
    /* This makes sure long names don't push the buttons down */
    .veg-name {
        height: 50px;
        line-height: 25px;
        overflow: hidden;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")
st.markdown("---")

# --- 3. DISPLAY PRODUCTS ---
df = load_data()

if df is not None:
    target_categories = ["Leafy Vegetables", "Root Vegetables", "General Vegetables"]
    
    for cat in target_categories:
        cat_df = df[df['category'] == cat]
        
        if not cat_df.empty:
            st.header(f"🛒 {cat}")
            
            cols = st.columns(3)
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    # Using border=True to keep each item in a clean box
                    with st.container(border=True):
                        name = row['name']
                        price = row['price']
                        unit = row['unit']
                        available = str(row['is_available']).upper() == "TRUE"
                        
                        if not available:
                            st.write(f"### ~~{name}~~")
                            st.error("Out of Stock")
                        else:
                            # --- IMAGE LOGIC ---
                            clean_name = name.lower().strip()
                            underscore_name = clean_name.replace(' ', '_')
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
                                # Placeholder box to keep height consistent even if image is missing
                                st.markdown("<div style='height:200px; background-color:#333; border-radius:5px; display:flex; align-items:center; justify-content:center;'>📷 Image Needed</div>", unsafe_allow_html=True)
                            
                            # --- PERFECTLY ALIGNED TITLES ---
                            st.markdown(f"<div class='veg-name'><h3>{name}</h3></div>", unsafe_allow_html=True)
                            
                            st.info(f"₹{price} / {unit}")
                            
                            qty = st.number_input(f"Amount", min_value=0.0, step=0.5, key=f"q_{name}")
                            if st.button(f"Add {name}", key=f"b_{name}", use_container_width=True):
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
    MY_NUMBER = "919948807525" 
    
    final_msg = urllib.parse.quote(order_msg + f"\n*Grand Total: ₹{total_bill}*")
    wa_url = f"https://wa.me/{MY_NUMBER}?text={final_msg}"
    
    st.sidebar.link_button("🚀 Send Order to WhatsApp", wa_url, use_container_width=True)
    
    if st.sidebar.button("Clear Cart", use_container_width=True):
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.write("Your cart is empty.")

st.sidebar.markdown("---")
st.sidebar.caption("Dakoju Vasantha Vidya Sagar")
