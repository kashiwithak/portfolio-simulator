
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Custom Portfolio Profit Simulator", layout="centered")
st.title("📊 Custom Portfolio Profit Tracker")

st.markdown("Add your holdings, set a goal, and track your potential profit.")

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

# Load profiles into memory
profiles = load_profiles()

# Select or create profile
st.sidebar.header("👤 User Profile")
username = st.sidebar.text_input("Enter your username", value="default_user")

if username in profiles:
    user_data = profiles[username]
    st.sidebar.success("Profile loaded.")
else:
    user_data = {
        "goal": 1000000,
        "assets": [
            {"name": "TSLA", "amount": 760, "avg_price": 350, "target_price": 700},
            {"name": "BTC", "amount": 0.538, "avg_price": 61000, "target_price": 229000},
            {"name": "ALGO", "amount": 42000, "avg_price": 0.2, "target_price": 3}
        ]
    }

profit_goal = st.number_input("Enter your profit goal ($):", min_value=0, value=user_data.get("goal", 1000000), step=10000)

st.subheader("📥 Asset Inputs with Target Sliders")

updated_assets = []
for i, asset in enumerate(user_data["assets"]):
    st.markdown(f"**{asset['name']}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        amount = st.number_input(f"{asset['name']} Amount", value=float(asset["amount"]), key=f"amt_{i}")
    with col2:
        avg_price = st.number_input(f"{asset['name']} Avg Price", value=float(asset["avg_price"]), key=f"avg_{i}")
    with col3:
        target_price = st.slider(f"{asset['name']} Target Price", min_value=0.0, max_value=2.0 * float(asset["target_price"]), value=float(asset["target_price"]), step=0.1, key=f"slider_{i}")
    updated_assets.append({
        "name": asset["name"],
        "amount": amount,
        "avg_price": avg_price,
        "target_price": target_price
    })

# Save profile button
if st.button("💾 Save Profile"):
    profiles[username] = {
        "goal": profit_goal,
        "assets": updated_assets
    }
    save_profiles(profiles)
    st.success("Profile saved!")

# Calculate portfolio
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
