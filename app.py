
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Portfolio Profit Simulator", layout="centered")
st.title("📈 $1M Profit Goal Tracker")

st.markdown("Adjust your target prices to see projected returns.")

# Initial investment data
data = {
    'Asset': ['TSLA', 'TSLL', 'BTC', 'ALGO'],
    'Amount': [760, 1920, 0.53813607, 42000],
    'Avg Price': [350, 23, 61000, 0.2],
    'Initial Investment': [266000, 44160, 32824, 8400]
}

assets = pd.DataFrame(data)

# Target sliders
st.sidebar.header("🎯 Target Prices")
tsla_target = st.sidebar.slider("TSLA Target Price", 200, 1200, 700)
tsll_target = st.sidebar.slider("TSLL Target Price", 10, 60, 29)
btc_target = st.sidebar.slider("BTC Target Price", 20000, 400000, 229000)
algo_target = st.sidebar.slider("ALGO Target Price", 0.1, 10.0, 3.0, step=0.1)

# Calculate new values
assets.loc[0, 'Target Value'] = tsla_target * assets.loc[0, 'Amount']
assets.loc[1, 'Target Value'] = tsll_target * assets.loc[1, 'Amount']
assets.loc[2, 'Target Value'] = btc_target * assets.loc[2, 'Amount']
assets.loc[3, 'Target Value'] = algo_target * assets.loc[3, 'Amount']

assets['Profit'] = assets['Target Value'] - assets['Initial Investment']
assets['ROI (%)'] = (assets['Profit'] / assets['Initial Investment']) * 100

# Portfolio totals
total_initial = assets['Initial Investment'].sum()
total_target = assets['Target Value'].sum()
total_profit = total_target - total_initial
total_roi = (total_profit / total_initial) * 100

# Display results
st.subheader("📊 Portfolio Breakdown")
st.dataframe(assets[['Asset', 'Amount', 'Initial Investment', 'Target Value', 'Profit', 'ROI (%)']], use_container_width=True)

st.subheader("💰 Summary")
st.metric("Initial Investment", f"${total_initial:,.0f}")
st.metric("Projected Value", f"${total_target:,.0f}")
st.metric("Projected Profit", f"${total_profit:,.0f}")
st.metric("ROI", f"{total_roi:.1f}%")

# Profit goal check
if total_profit >= 1_000_000:
    st.success("🎉 You reached your $1M profit goal!")
else:
    st.info(f"You need ${1_000_000 - total_profit:,.0f} more in profit to hit your $1M goal.")
