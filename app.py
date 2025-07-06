
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")
st.title("📈 Portfolio Profit Simulator")

DATA_FILE = Path("profiles.json")

def load_profiles():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(DATA_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

def calculate_portfolio_metrics(assets):
    if not assets:
        return None, 0, 0, 0, 0
    df = pd.DataFrame(assets)
    df["Initial Investment"] = df["amount"] * df["avg_price"]
    df["Target Value"] = df["amount"] * df["target_price"]
    df["Profit"] = df["Target Value"] - df["Initial Investment"]
    df["ROI (%)"] = (df["Profit"] / df["Initial Investment"]) * 100

    total_initial = df["Initial Investment"].sum()
    total_target = df["Target Value"].sum()
    total_profit = total_target - total_initial
    total_roi = (total_profit / total_initial) * 100

    return df, total_initial, total_target, total_profit, total_roi

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

# Setup session state
if "assets" not in st.session_state:
    st.session_state.assets = user_data.get("assets", [])
if "goal" not in st.session_state:
    st.session_state.goal = user_data.get("goal", 1000000)
if "remove_flags" not in st.session_state:
    st.session_state.remove_flags = [False] * len(st.session_state.assets)

# Profit goal input
st.subheader("🎯 Profit Goal")
profit_goal = st.number_input("Target Profit ($)", min_value=0, value=st.session_state.goal, step=10000)

# Calculate summary before editing
df_preview, total_initial, total_target, total_profit, total_roi = calculate_portfolio_metrics(
    [asset for i, asset in enumerate(st.session_state.assets) if not st.session_state.remove_flags[i]]
)

if df_preview is not None:
    st.markdown("### 💰 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Initial Investment", f"${total_initial:,.0f}")
    col2.metric("Projected Value", f"${total_target:,.0f}")
    col3.metric("Projected Profit", f"${total_profit:,.0f}")
    col4.metric("ROI", f"{total_roi:.1f}%")

    if total_profit >= profit_goal:
        st.success(f"🎉 You hit your ${profit_goal:,.0f} profit goal!")
    else:
        st.info(f"You're ${profit_goal - total_profit:,.0f} away from your profit target.")
else:
    st.warning("Add assets to begin building your portfolio.")

# Add asset block
st.sidebar.subheader("➕ Add New Asset")
with st.sidebar.form("add_asset_form"):
    new_name = st.text_input("Asset Symbol").upper()
    new_amount = st.number_input("Amount Held", min_value=0.0, step=1.0)
    new_avg_price = st.number_input("Average Price Paid", min_value=0.0, step=1.0)
    default_max_price = new_avg_price * 5 if new_avg_price > 0 else 5.0
    new_max_price = st.number_input("Max Target Price", min_value=1.0, value=default_max_price, step=1.0)
    if st.form_submit_button("Add Asset") and new_name:
        st.session_state.assets.append({
            "name": new_name,
            "amount": new_amount,
            "avg_price": new_avg_price,
            "target_price": new_avg_price * 2,
            "max_price": new_max_price
        })
        st.session_state.remove_flags.append(False)
        st.success(f"{new_name} added!")

# Edit/remove assets
st.subheader("📊 Portfolio Overview")
updated_assets = []

for i, asset in enumerate(st.session_state.assets):
    if st.session_state.remove_flags[i]:
        continue

    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    with col1:
        st.markdown(f"**{asset['name']}**")
    with col2:
        amount = st.number_input(f"{asset['name']} Amount", value=asset["amount"], key=f"amt_{i}")
    with col3:
        avg_price = st.number_input(f"{asset['name']} Avg Price", value=asset["avg_price"], key=f"avg_{i}")
    with col4:
        max_slider = st.number_input(f"{asset['name']} Max Target", value=asset.get("max_price", avg_price * 5), key=f"max_{i}")
    with col5:
        if st.button("❌", key=f"remove_{i}"):
            st.session_state.remove_flags[i] = True
            st.rerun()

    st.markdown("#### 🎯 Target Price")
    target_price = st.slider(
        f"{asset['name']} Target Price",
        min_value=0.1,
        max_value=max_slider,
        value=asset["target_price"],
        step=10000.0,
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
    st.session_state.remove_flags = [False] * len(updated_assets)
    profiles[username] = {
        "goal": profit_goal,
        "assets": updated_assets
    }
    save_profiles(profiles)
    st.success("Profile saved!")

# Display full breakdown table
if updated_assets:
    df, *_ = calculate_portfolio_metrics(updated_assets)
    st.markdown("### 📈 Portfolio Breakdown")
    st.dataframe(df[["name", "amount", "avg_price", "target_price", "Initial Investment", "Target Value", "Profit", "ROI (%)"]], use_container_width=True)
