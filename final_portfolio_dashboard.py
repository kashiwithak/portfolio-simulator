
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")
st.title("📈 Portfolio Profit Simulator")

DATA_FILE = Path("profiles.json")

# Load/save profile functions
def load_profiles():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(DATA_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

# Load user profiles
profiles = load_profiles()

# Sidebar: User & goal
st.sidebar.header("👤 User Profile")
username = st.sidebar.text_input("Enter your username", value="default_user")

if username in profiles:
    user_data = profiles[username]
    st.sidebar.success("Profile loaded.")
else:
    user_data = {
        "goal": 1000000,
        "assets": []
    }

# Initialize session state
if "assets" not in st.session_state:
    st.session_state.assets = user_data.get("assets", [])
if "goal" not in st.session_state:
    st.session_state.goal = user_data.get("goal", 1000000)

# Editable goal
st.sidebar.subheader("🎯 Profit Goal")
profit_goal = st.sidebar.number_input("Target Profit ($)", min_value=0, value=st.session_state.goal, step=10000)

# Add new asset section
with st.sidebar.expander("➕ Add New Asset", expanded=False):
    new_name = st.text_input("Asset Symbol", key="new_symbol").upper()
    new_amount = st.number_input("Amount Held", min_value=0.0, step=1.0, key="new_amt")
    new_avg_price = st.number_input("Average Price Paid", min_value=0.0, step=1.0, key="new_avg")
    if st.button("Add Asset", key="add_asset"):
        if new_name:
            st.session_state.assets.append({
                "name": new_name,
                "amount": new_amount,
                "avg_price": new_avg_price,
                "target_price": new_avg_price * 2,
                "max_price": new_avg_price * 5
            })
            st.success(f"{new_name} added to portfolio!")

# Portfolio editor
st.subheader("📊 Portfolio Overview")

updated_assets = []
cols = st.columns([3, 3, 3, 3, 1])

for i, asset in enumerate(st.session_state.assets):
    with cols[0]:
        st.markdown(f"**{asset['name']}**")
    with cols[1]:
        amount = st.number_input(f"{asset['name']} Amount", value=asset["amount"], key=f"amt_{i}")
    with cols[2]:
        avg_price = st.number_input(f"{asset['name']} Avg Price", value=asset["avg_price"], key=f"avg_{i}")
    with cols[3]:
        max_slider = st.number_input(f"{asset['name']} Max Target", value=asset.get("max_price", avg_price * 5), key=f"max_{i}")
    with cols[4]:
        if st.button("❌", key=f"remove_{i}"):
            continue  # skip adding to updated_assets (removes it)
    target_price = st.slider(
        f"{asset['name']} Target Price",
        min_value=0.1,
        max_value=max_slider,
        value=asset["target_price"],
        step=0.1,
        key=f"slider_{i}"
    )
    updated_assets.append({
        "name": asset["name"],
        "amount": amount,
        "avg_price": avg_price,
        "target_price": target_price,
        "max_price": max_slider
    })

# Save profile
if st.button("💾 Save Profile"):
    st.session_state.goal = profit_goal
    st.session_state.assets = updated_assets
    profiles[username] = {
        "goal": profit_goal,
        "assets": updated_assets
    }
    save_profiles(profiles)
    st.success("Profile saved!")

# Portfolio calculation
if updated_assets:
    df = pd.DataFrame(updated_assets)
    df["Initial Investment"] = df["amount"] * df["avg_price"]
    df["Target Value"] = df["amount"] * df["target_price"]
    df["Profit"] = df["Target Value"] - df["Initial Investment"]
    df["ROI (%)"] = (df["Profit"] / df["Initial Investment"]) * 100

    total_initial = df["Initial Investment"].sum()
    total_target = df["Target Value"].sum()
    total_profit = total_target - total_initial
    total_roi = (total_profit / total_initial) * 100

    st.markdown("### 📈 Portfolio Breakdown")
    st.dataframe(df[["name", "amount", "avg_price", "target_price", "Initial Investment", "Target Value", "Profit", "ROI (%)"]], use_container_width=True)

    st.markdown("### 💰 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Initial Investment", f"${total_initial:,.0f}")
    col2.metric("Projected Value", f"${total_target:,.0f}")
    col3.metric("Projected Profit", f"${total_profit:,.0f}")
    col4.metric("ROI", f"{total_roi:.1f}%")

    if total_profit >= profit_goal:
        st.success(f"🎉 Congrats! You hit your ${profit_goal:,.0f} profit goal.")
    else:
        st.info(f"You're ${profit_goal - total_profit:,.0f} away from your profit target.")
else:
    st.warning("Add assets to begin building your portfolio.")
