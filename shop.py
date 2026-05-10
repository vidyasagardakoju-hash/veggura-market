import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. DATA CONNECTION ---
SHEET_ID = "1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6"
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-{SHEET_ID}/pub?output=csv"

def load_data():
    try:
        # Added cache breaker to ensure data updates instantly
        df = pd.read_csv(f"{CSV_URL}&t={pd.Timestamp.now().timestamp()}")
        df.columns = df.columns.str.strip()
        df['category'] = df['category'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")
st.markdown("---")

# --- 3. DISPLAY PRODUCTS (Restored Layout) ---
df = load_data()

if df is not None:
    # We specify your 3 categories in order to keep the layout clean
    target_categories = ["Leafy Vegetables", "Root Vegetables", "General Vegetables"]
    
    for cat in target_categories:
        cat_df = df[df['category'] == cat]
        
        if not cat_df.empty:
            st.header(f"🛒 {cat}")
            
            # The 3-column grid you loved
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
                        # --- RESTORED IMAGE LOGIC ---
                        # Looks for 'tomato.jpg' in your GitHub main folder
                        img_path = f"{name.lower().replace(' ', '_')}.jpg"
                        try:
                            st.image(img_path, width=200)
                        except:
                            st.write("📷 Image Pending")
                            
                        st.write(f"### {name}")
                        st.info(f"₹{price} / {unit}")
                        
                        qty = st.number_input(f"Amount ({unit})", min_value=0.0, step=0.5, key=f"q_{name}")
                        if st.button(f"Add {name}", key=f"b_{name}"):
                            if qty > 0:
                                st.session_state.cart[name] = {"qty": qty, "total": qty * price, "unit": unit}
                                st.toast(f"✅ {name} added!")
            st.markdown("---")

# --- 4. SIDEBAR & WHATSAPP (Professional Version) ---
st.sidebar.header("📋 Your Order Summary")

if st.session_state.cart:
    total_bill = 0
    order_msg = "Hello Veggura! I want to order:\n\n"
    
    for item, d in st.session_state.cart.items():
        line = f"• {item}: {d['qty']} {d['unit']} - ₹{d['total']}\n"
        st.sidebar.write(line)
        order_msg += line
        total_bill += d['total']
    
    st.sidebar.subheader(f"Total: ₹{total_bill}")
    
    # --- REPLACE WITH YOUR NUMBER ---
    MY_NUMBER = "91XXXXXXXXXX" 
    
    final_msg = urllib.parse.quote(order_msg + f"\n*Grand Total: ₹{total_bill}*")
    wa_url = f"https://wa.me/{MY_NUMBER}?text={final_msg}"
    
    st.sidebar.link_button("🚀 Place Order via WhatsApp", wa_url, use_container_width=True)
    
    if st.sidebar.button("Clear Cart"):
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.write("Cart is empty. Add fresh veggies to start!")
