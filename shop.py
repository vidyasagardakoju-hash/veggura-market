import streamlit as st
import pandas as pd

# --- YOUR REAL LINK ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6/pubhtml"

def load_data():
    # Correctly handles the /pubhtml link for CSV export
    csv_url = SHEET_URL.replace("/pubhtml", "/pub?output=csv")
    df = pd.read_csv(csv_url)
    
    # Matching your Google Sheet column names to the code's names
    df = df.rename(columns={'price': 'price_per_kg', 'unit': 'unit_type'})
    
    # Ensuring is_available is handled as 1 (True) or 0 (False)
    df['is_available'] = df['is_available'].astype(str).str.upper().map({'TRUE': 1, 'FALSE': 0, '1': 1, '0': 0})
    return df

# --- APP CONFIG ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")
st.write("Fresh produce from our mandi to your home.")

try:
    df = load_data()
    
    # --- FIXED CATEGORIES SECTION ---
    categories_to_display = {
        "Leafy Vegetables": "🥬 Leafy Vegetables",
        "Root Vegetables": "🥕 Root Vegetables",
        "Vegetables": "🥦 General Vegetables"
    }

    for cat_key, cat_label in categories_to_display.items():
        cat_df = df[df['category'] == cat_key]
        
        if not cat_df.empty:
            st.header(cat_label)
            cols = st.columns(3)
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    name = row['name']
                    if row['is_available'] == 0:
                        st.write(f"### ~~{name}~~")
                        st.error("Out of Stock")
                    else:
                        try: 
                            st.image(f"{name.lower()}.jpg", use_container_width=True)
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

    # --- SIDEBAR CART & WHATSAPP ---
    st.sidebar.header("📋 Your Order")
    total_bill = 0
    order_text = "New Order from Veggura:%0A"

    if not st.session_state.cart:
        st.sidebar.write("Your cart is empty.")
    else:
        for item, details in st.session_state.cart.items():
            st.sidebar.write(f"**{item}**: {details['qty']} {details['unit']} - ₹{details['total']}")
            total_bill += details['total']
            order_text += f"- {item}: {details['qty']} {details['unit']} (₹{details['total']})%0A"
        
        st.sidebar.write("---")
        st.sidebar.write(f"### Total Bill: ₹{total_bill}")
        
        # Replace with your phone number (e.g., 919876543210)
        my_phone = "91XXXXXXXXXX" 
        
        order_text += f"%0A---%0ATotal Bill: ₹{total_bill}"
        wa_link = f"https://wa.me/{my_phone}?text={order_text}"
        
        st.sidebar.markdown(f'''
            <a href="{wa_link}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;">
                    Confirm Order on WhatsApp
                </div>
            </a>
        ''', unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ App Error: {e}")
