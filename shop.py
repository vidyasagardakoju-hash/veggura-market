import streamlit as st
import pandas as pd

# --- GOOGLE SHEET CONNECTION ---
# This is your published CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6/pubhtml"

def load_data():
    # Convert the web link to a CSV download link
    csv_url = SHEET_URL.replace("/pubhtml", "/pub?output=csv")
    df = pd.read_csv(csv_url)
    # Standardize column names for the app
    df = df.rename(columns={'price': 'price_per_kg', 'unit': 'unit_type'})
    # Convert text TRUE/FALSE to numbers 1/0
    df['is_available'] = df['is_available'].astype(str).str.upper().map({'TRUE': 1, 'FALSE': 0, '1': 1, '0': 0})
    return df

# --- APP CONFIG ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

# Initialize Session States
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# Load the fresh data from Google Sheets
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading Google Sheet: {e}")
    st.stop()

# --- STEP 1: CATEGORY HOME SCREEN ---
if st.session_state.page == "home":
    st.title("🥦 Veggura Local Market")
    st.subheader("Select a category to view fresh produce:")
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h1 style='text-align: center;'>🥬</h1>", unsafe_allow_html=True)
        if st.button("Leafy Vegetables", use_container_width=True):
            st.session_state.page = "Leafy Vegetables"
            st.rerun()
            
    with col2:
        st.markdown("<h1 style='text-align: center;'>🥕</h1>", unsafe_allow_html=True)
        if st.button("Root Vegetables", use_container_width=True):
            st.session_state.page = "Root Vegetables"
            st.rerun()
            
    with col3:
        st.markdown("<h1 style='text-align: center;'>🍅</h1>", unsafe_allow_html=True)
        if st.button("General Vegetables", use_container_width=True):
            st.session_state.page = "General Vegetables"
            st.rerun()

# --- STEP 2: PRODUCT LISTING PAGE ---
else:
    selected_cat = st.session_state.page
    
    # Back Navigation
    if st.button("⬅️ Back to Categories"):
        st.session_state.page = "home"
        st.rerun()
        
    st.title(f"🛒 {selected_cat}")
    
    # Filter products by the chosen category
    cat_df = df[df['category'] == selected_cat]
    
    if cat_df.empty:
        st.warning(f"No items currently available in {selected_cat}.")
    else:
        cols = st.columns(3)
        for idx, row in cat_df.reset_index(drop=True).iterrows():
            with cols[idx % 3]:
                # Image search (expects filename like tomato.jpg)
                try:
                    st.image(f"{row['name'].lower()}.jpg", use_container_width=True)
                except:
                    st.write("📷 Photo Coming Soon")
                
                st.subheader(row['name'])
                
                if row['is_available'] == 0:
                    st.error("Out of Stock")
                else:
                    st.info(f"₹{row['price_per_kg']} per {row['unit_type']}")
                    qty = st.number_input(f"Qty", min_value=0.0, step=0.5, key=f"buy_{row['name']}")
                    if st.button(f"Add {row['name']}", key=f"btn_{row['name']}"):
                        if qty > 0:
                            st.session_state.cart[row['name']] = {
                                "qty": qty, 
                                "total": qty * row['price_per_kg'], 
                                "unit": row['unit_type']
                            }
                            st.toast(f"Added {row['name']}!")

# --- SIDEBAR CART ---
st.sidebar.header("📋 Your Order")
if not st.session_state.cart:
    st.sidebar.write("Your cart is empty.")
else:
    total_bill = 0
    order_summary = "New Order from Veggura:%0A"
    
    for item, d in st.session_state.cart.items():
        st.sidebar.write(f"**{item}**: {d['qty']} {d['unit']} - ₹{d['total']}")
        total_bill += d['total']
        order_summary += f"- {item}: {d['qty']} {d['unit']} (₹{d['total']})%0A"
    
    st.sidebar.write("---")
    st.sidebar.write(f"### Total: ₹{total_bill}")
    
    # CUSTOMER CONTACT (Replace with your actual number)
    my_phone = "91XXXXXXXXXX" 
    
    wa_link = f"https://wa.me/{my_phone}?text={order_summary}%0ATotal: ₹{total_bill}"
    st.sidebar.markdown(f'''
        <a href="{wa_link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;">
                Confirm Order on WhatsApp
            </div>
        </a>
    ''', unsafe_allow_html=True)
    
    if st.sidebar.button("🗑️ Clear Cart"):
        st.session_state.cart = {}
        st.rerun()
