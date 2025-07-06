
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Custom Portfolio Profit Simulator", layout="centered")
st.title("📊 Custom Portfolio Profit Tracker")

st.markdown("Add your holdings, set a goal, and track your potential profit.")

# Input: Set profit goal
profit_goal = st.number_input("Enter your profit goal ($):", min_value=0, value=1000000, step=10000)

# Input: Add custom assets
st.subheader("📥 Enter Your Assets")

with st.form("asset_form"):
    asset_names = st.text_area("Asset Names (comma separated)", value="TSLA, BTC, ALGO")
    asset_amounts = st.text_area("Amounts Held (comma separated)", value="760, 0.538, 42000")
    asset_avg_prices = st.text_area("Average Prices Paid (comma separated)", value="350, 61000, 0.2")
    asset_target_prices = st.text_area("Target Prices (comma separated)", value="700, 229000, 3")
    submitted = st.form_submit_button("Update Portfolio")

if submitted:
    try:
        names = [x.strip().upper() for x in asset_names.split(',')]
        amounts = [float(x.strip()) for x in asset_amounts.split(',')]
        avg_prices = [float(x.strip()) for x in asset_avg_prices.split(',')]
        targets = [float(x.strip()) for x in asset_target_prices.split(',')]

        if not (len(names) == len(amounts) == len(avg_prices) == len(targets)):
            st.error("All fields must have the same number of entries.")
        else:
            df = pd.DataFrame({
                'Asset': names,
                'Amount': amounts,
                'Avg Price': avg_prices,
                'Target Price': targets
            })

            df['Initial Investment'] = df['Amount'] * df['Avg Price']
            df['Target Value'] = df['Amount'] * df['Target Price']
            df['Profit'] = df['Target Value'] - df['Initial Investment']
            df['ROI (%)'] = (df['Profit'] / df['Initial Investment']) * 100

            total_initial = df['Initial Investment'].sum()
            total_target = df['Target Value'].sum()
            total_profit = total_target - total_initial
            total_roi = (total_profit / total_initial) * 100

            st.subheader("📈 Portfolio Breakdown")
            st.dataframe(df[['Asset', 'Amount', 'Avg Price', 'Target Price', 'Initial Investment', 'Target Value', 'Profit', 'ROI (%)']], use_container_width=True)

            st.subheader("💰 Summary")
            st.metric("Initial Investment", f"${total_initial:,.0f}")
            st.metric("Projected Value", f"${total_target:,.0f}")
            st.metric("Projected Profit", f"${total_profit:,.0f}")
            st.metric("ROI", f"{total_roi:.1f}%")

            if total_profit >= profit_goal:
                st.success(f"🎉 You reached your ${profit_goal:,.0f} profit goal!")
            else:
                st.info(f"You need ${profit_goal - total_profit:,.0f} more in profit to hit your goal.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.info("Enter your asset data and click 'Update Portfolio' to begin.")
