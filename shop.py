import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. GOOGLE SHEET CONNECTION ---
# Using the direct export link we verified
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6/export?format=csv"

def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Clean up column names and text to avoid errors with hidden spaces
        df.columns = df.columns.str.strip()
        df['category'] = df['category'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Could not read the sheet: {e}")
        return None

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")

# --- 3. LOAD DATA ---
df = load_data()

if df is not None:
    # DEBUG: This will show you exactly what categories the computer found
    # You can remove this line once it's working!
    st.write("Found categories:", df['category'].unique().tolist())
    
    # We will loop through every category that actually exists in your sheet
    for cat in df['category'].unique():
        st.header(f"🛒 {cat}")
        cat_df = df[df['category'] == cat]
        
        cols = st.columns(3)
        for index, row in cat_df.reset_index(drop=True).iterrows():
            with cols[index % 3]:
                name = row['name']
                price = row['price']
                unit = row['unit']
                
                st.write(f"### {name}")
                st.info(f"₹{price} per {unit}")
                
                qty = st.number_input(f"Qty ({unit})", min_value=0.0, step=0.5, key=f"qty_{name}")
                
                if st.button(f"Add {name}", key=f"btn_{name}"):
                    if qty > 0:
                        st.session_state.cart[name] = {"qty": qty, "total": qty * price, "unit": unit}
                        st.toast(f"Added {name}!")
        st.markdown("---")

# --- 4. SIDEBAR ORDERING ---
st.sidebar.header("📋 Your Order")
if st.session_state.cart:
    total_bill = 0
    order_details = "Hello Veggura! New Order:\n\n"
    for item, d in st.session_state.cart.items():
        line = f"• {item}: {d['qty']} {d['unit']} - ₹{d['total']}\n"
        st.sidebar.write(line)
        order_details += line
        total_bill += d['total']
    
    st.sidebar.subheader(f"Total: ₹{total_bill}")
    
    # REPLACE WITH YOUR REAL NUMBER
    MY_PHONE_NUMBER = "91XXXXXXXXXX" 
    wa_link = f"https://wa.me/{MY_PHONE_NUMBER}?text={urllib.parse.quote(order_details + f'Total: ₹{total_bill}')}"
    st.sidebar.link_button("🚀 Order on WhatsApp", wa_link, use_container_width=True)
else:
    st.sidebar.write("Cart is empty.")
