import streamlit as st
import pandas as pd

# --- YOUR REAL LINK ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6/pubhtml"

def load_data():
    # This logic handles the /pubhtml link correctly
    csv_url = SHEET_URL.replace("/pubhtml", "/pub?output=csv")
    df = pd.read_csv(csv_url)
    
    # Matching your Google Sheet column names to the code's names
    df = df.rename(columns={
        'price': 'price_per_kg',
        'unit': 'unit_type'
    })
    
    # Ensuring is_available is handled as 1 (True) or 0 (False)
    df['is_available'] = df['is_available'].astype(str).str.upper().map({'TRUE': 1, 'FALSE': 0, '1': 1, '0': 0})
    return df

st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")

try:
    df = load_data()
    target_categories = ["Leafy Vegetables", "Root Vegetables", "Vegetables"]

    for cat in target_categories:
        cat_df = df[df['category'] == cat]
        if not cat_df.empty:
            st.header(f"🛒 {cat}")
            cols = st.columns(3)
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    name = row['name']
                    # logic for availability
                    if row['is_available'] == 0:
                        st.write(f"### ~~{name}~~")
                        st.error("Out of Stock")
                    else:
                        # Image logic: looking for name.jpg in your GitHub folder
                        try: 
                            st.image(f"{name.lower()}.jpg", width=150)
                        except: 
                            st.write("📷 Image Pending")
                        
                        st.write(f"### {name}")
                        st.info(f"₹{row['price_per_kg']} per {row['unit_type']}")
                        
                        qty = st.number_input(f"Qty", min_value=0.0, step=0.5, key=f"shop_{name}")
                        if st.button(f"Add {name}", key=f"btn_{name}"):
                            if qty > 0:
                                st.session_state.cart[name] = {"qty": qty, "total": qty * row['price_per_kg'], "unit": row['unit_type']}
                                st.toast(f"Added {name}!")
            st.write("---")

    # --- SIDEBAR CART ---
    st.sidebar.header("📋 Your Order")
    total_bill = 0
    if not st.session_state.cart:
        st.sidebar.write("Cart is empty.")
    else:
        for item, d in st.session_state.cart.items():
            st.sidebar.write(f"**{item}**: {d['qty']} {d['unit']} - ₹{d['total']}")
            total_bill += d['total']
        
        st.sidebar.write(f"### Total: ₹{total_bill}")
        
        # WhatsApp Integration (Replace with your number)
        my_phone = "91XXXXXXXXXX" 
        wa_link = f"https://wa.me/{my_phone}?text=New Order from Veggura"
        st.sidebar.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">Order on WhatsApp</button></a>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Waiting for Data... (Error: {e})")
