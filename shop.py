import streamlit as st
import sqlite3
import pandas as pd

# --- DATABASE FUNCTION ---
def load_data():
    conn = sqlite3.connect('veggura_market.db')
    # Fetching all columns to support categorization and availability checks
    df = pd.read_sql_query("SELECT id, name, category, price_per_kg, unit_type, is_available FROM inventory", conn)
    conn.close()
    return df

# --- APP CONFIG ---
st.set_page_config(page_title="Veggura Market", page_icon="🥦", layout="wide")

# --- SESSION STATE FOR CART ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- MAIN SHOP INTERFACE ---
st.title("🥦 Veggura Local Market")
st.write("Fresh produce categorized for your convenience.")

try:
    df = load_data()
    
    # The three specific sections you requested
    target_categories = ["Leafy Vegetables", "Root Vegetables", "Vegetables"]

    for cat in target_categories:
        # Filter the data for the specific category
        cat_df = df[df['category'] == cat]
        
        if not cat_df.empty:
            st.header(f"🛒 {cat}")
            
            # Create a 3-column grid for the items
            cols = st.columns(3)
            for index, row in cat_df.reset_index(drop=True).iterrows():
                with cols[index % 3]:
                    name = row['name']
                    unit = row['unit_type']
                    price = row['price_per_kg']
                    
                    # 1. Check if the item is marked as Unavailable in Admin
                    if row['is_available'] == 0:
                        st.write(f"### ~~{name}~~")
                        st.error("Currently Unavailable")
                    else:
                        # 2. Try to load the image (name must match lowercase filename)
                        img_path = f"{name.lower()}.jpg"
                        try: 
                            st.image(img_path, width=150)
                        except: 
                            st.write("📷 No Image Found")
                        
                        st.write(f"### {name}")
                        st.info(f"₹{price} per {unit}")
                        
                        # 3. Quantity input (1.0 for pieces/bunches, 0.5 for kg)
                        step = 1.0 if unit in ["Piece", "Dozen", "Bunch"] else 0.5
                        qty = st.number_input(f"Qty ({unit})", min_value=0.0, step=step, key=f"shop_{name}")
                        
                        # 4. Add to Cart logic
                        if st.button(f"Add {name}", key=f"btn_{name}"):
                            if qty > 0:
                                st.session_state.cart[name] = {
                                    "qty": qty, 
                                    "total": qty * price, 
                                    "unit": unit
                                }
                                st.toast(f"Added {qty} {unit} of {name}!")
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
        
        # !!! REPLACE WITH YOUR ACTUAL WHATSAPP NUMBER !!!
        my_phone = "91XXXXXXXXXX" 
        
        order_text += f"%0A---%0ATotal Bill: ₹{total_bill}"
        wa_link = f"https://wa.me/{my_phone}?text={order_text}"
        
        # WhatsApp Green Checkout Button
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

except Exception as e:
    st.error(f"⚠️ App Error: {e}")
    st.info("Ensure you have set the Categories and Status in the Admin panel (Port 9999).")