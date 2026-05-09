import streamlit as st
import pandas as pd
import urllib.parse

# --- 1. GOOGLE SHEET CONNECTION ---
# Replace the URL below with your "Publish to Web" link from Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4lFwEMAaEQJc3ogMb0gVm913bIVIXkRNjgSvCEUNWo0GSuHbj4uY0nDqlZR16BfAGlZUaxpk0GpL6/pubhtm"

def load_data():
    try:
        # Converts the public link into a CSV download link for Pandas
        csv_url = SHEET_URL.replace("/pubhtml", "/export?format=csv")
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error("Connection Error: Please check if your Google Sheet is 'Published to web'.")
        return None

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

# Initialize the shopping cart in the session
if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.title("🥦 Veggura Local Market")
st.markdown("---")

# --- 3. LOAD & DISPLAY PRODUCTS ---
df = load_data()

if df is not None:
    # Categories as per your business layout
    target_categories = ["Leafy Vegetables", "Root Vegetables", "Vegetables"]

    for cat in target_categories:
        # Filter data for this specific category
        cat_df = df[df['category'] == cat]
        
        if not cat_df.empty:
            st.header(f"🛒 {cat}")
            
            # Create a 3-column grid for products
            cols = st.columns(3)
            
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    name = row['name']
                    price = row['price']
                    unit = row['unit']
                    is_available = row['is_available']
                    
                    # If item is unavailable, show it as grayed out
                    if not is_available:
                        st.write(f"### ~~{name}~~")
                        st.error("Out of Stock")
                    else:
                        # Display Product Image (looks for name.jpg in your GitHub repo)
                        try:
                            st.image(f"{name.lower()}.jpg", width=180)
                        except:
                            st.write("📷 Image Pending")
                        
                        st.write(f"### {name}")
                        st.info(f"₹{price} per {unit}")
                        
                        # Quantity Selector
                        qty = st.number_input(f"Quantity ({unit})", min_value=0.0, step=0.5, key=f"qty_{name}")
                        
                        if st.button(f"Add {name} to Cart", key=f"btn_{name}"):
                            if qty > 0:
                                st.session_state.cart[name] = {
                                    "qty": qty, 
                                    "total": qty * price, 
                                    "unit": unit
                                }
                                st.toast(f"Added {name} to cart!")
            st.markdown("---")

# --- 4. SIDEBAR CART & WHATSAPP ORDERING ---
st.sidebar.header("📋 Your Order Summary")

if not st.session_state.cart:
    st.sidebar.write("Your cart is empty. Add some fresh veggies!")
else:
    total_bill = 0
    # Text for the WhatsApp message
    order_details = "Hello Veggura! I want to place an order:\n\n"
    
    for item, d in st.session_state.cart.items():
        line = f"• {item}: {d['qty']} {d['unit']} - ₹{d['total']}\n"
        st.sidebar.write(line)
        order_details += line
        total_bill += d['total']
    
    st.sidebar.subheader(f"Total: ₹{total_bill}")
    order_details += f"\n*Grand Total: ₹{total_bill}*"

    # Clear Cart Button
    if st.sidebar.button("🗑️ Clear Cart"):
        st.session_state.cart = {}
        st.rerun()

    # WhatsApp Link Generation
    # REPLACE THE NUMBER BELOW WITH YOUR 10-DIGIT NUMBER (Keep the 91)
    MY_PHONE_NUMBER = "919948807525" 
    encoded_msg = urllib.parse.quote(order_details)
    wa_link = f"https://wa.me/{MY_PHONE_NUMBER}?text={encoded_msg}"
    
    st.sidebar.link_button("🚀 Send Order to WhatsApp", wa_link, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Managed by Dakoju Vasantha Vidya Sagar")
