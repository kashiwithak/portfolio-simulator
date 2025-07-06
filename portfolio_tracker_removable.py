
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Portfolio Profit Simulator", layout="centered")
st.title("📊 Custom Portfolio Profit Tracker")

DATA_FILE = Path("profiles.json")

# Load existing profiles
def load_profiles():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save updated profiles
def save_profiles(profiles):
    with open(DATA_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

# Load or create profile
profiles = load_profiles()
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

# Goal input
profit_goal = st.number_input("Enter your profit goal ($):", min_value=0, value=st.session_state.goal, step=10000)

# Add new asset
st.subheader("➕ Add New Asset")
with st.form("add_asset_form"):
    new_name = st.text_input("Asset Symbol (e.g. AAPL, BTC)").upper()
    new_amount = st.number_input("Amount Held", min_value=0.0, step=1.0)
    new_avg_price = st.number_input("Average Price Paid", min_value=0.0, step=1.0)
    new_max_price = st.number_input("Max Slider Value for Target Price", min_value=1.0, value=new_avg_price * 5, step=1.0)
    submitted = st.form_submit_button("Add Asset")
    if submitted and new_name:
        st.session_state.assets.append({
            "name": new_name,
            "amount": new_amount,
            "avg_price": new_avg_price,
            "target_price": new_avg_price * 2,
            "max_price": new_max_price
        })
        st.success(f"{new_name} added!")

# Update and edit assets
st.subheader("📥 Portfolio Assets")

updated_assets = []
assets_to_remove = []

for i, asset in enumerate(st.session_state.assets):
    with st.expander(f"{asset['name']} Settings", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            amount = st.number_input(f"{asset['name']} Amount", value=asset["amount"], key=f"amt_{i}")
        with col2:
            avg_price = st.number_input(f"{asset['name']} Avg Price", value=asset["avg_price"], key=f"avg_{i}")
        with col3:
            max_slider = st.number_input(f"{asset['name']} Max Target", value=asset.get("max_price", avg_price * 5), key=f"max_{i}")
        with col4:
            target_price = st.slider(f"{asset['name']} Target", min_value=0.1, max_value=max_slider,
                                     value=asset["target_price"], step=0.1, key=f"slider_{i}")
        if st.button(f"🗑️ Remove {asset['name']}", key=f"remove_{i}"):
            assets_to_remove.append(i)
        else:
            updated_assets.append({
                "name": asset["name"],
                "amount": amount,
                "avg_price": avg_price,
                "target_price": target_price,
                "max_price": max_slider
            })

# Remove assets
if assets_to_remove:
    for index in sorted(assets_to_remove, reverse=True):
        del updated_assets[index]
    st.success("Selected asset(s) removed.")
    st.session_state.assets = updated_assets

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

# Calculate portfolio
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

    st.subheader("📈 Portfolio Breakdown")
    st.dataframe(df[["name", "amount", "avg_price", "target_price", "Initial Investment", "Target Value", "Profit", "ROI (%)"]], use_container_width=True)

    st.subheader("💰 Summary")
    st.metric("Initial Investment", f"${total_initial:,.0f}")
    st.metric("Projected Value", f"${total_target:,.0f}")
    st.metric("Projected Profit", f"${total_profit:,.0f}")
    st.metric("ROI", f"{total_roi:.1f}%")

    if total_profit >= profit_goal:
        st.success(f"🎉 You reached your ${profit_goal:,.0f} profit goal!")
    else:
        st.info(f"You need ${profit_goal - total_profit:,.0f} more in profit to hit your goal.")
else:
    st.info("Add assets to start calculating your portfolio.")
