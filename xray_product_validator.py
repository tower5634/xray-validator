import streamlit as st
import pandas as pd

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 🔍 Find the right column for Reviews
    for col in df.columns:
        if "review" in col.lower() and "count" in col.lower():
            df.rename(columns={col: "Reviews"}, inplace=True)
            break

    # 🔍 Find the right column for Revenue
    revenue_col = None
    for col in df.columns:
        if "revenue" in col.lower() and "parent" in col.lower():
            revenue_col = col
            break
    if not revenue_col:
        for col in df.columns:
            if "revenue" in col.lower():
                revenue_col = col
                break

    # 🔍 Find the right column for Price
    price_col = None
    for col in df.columns:
        if "price" in col.lower():
            price_col = col
            break

    st.subheader("Step 1: Success Rate")

    # Clean up the revenue and price columns
    if revenue_col:
        df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)  # Remove commas and currency symbols
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')  # Convert to numeric, invalid values become NaN

    if price_col:
        df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)  # Remove commas and currency symbols
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')  # Convert to numeric, invalid values become NaN

    try:
        total_sellers = df.shape[0]
        sellers_above_10k = df[df[revenue_col] > 10000].shape[0]
        success_rate = round((sellers_above_10k / total_sellers) * 100, 2)

        st.write(f"✅ Success Rate: **{success_rate}%** ({sellers_above_10k} out of {total_sellers} sellers over $10K revenue)")

        if success_rate >= 75:
            st.success("🎯 This product has a high success rate!")
        else:
            st.warning("⚠️ This product might not have a high enough success rate.")
    except Exception as e:
        st.error(f"❌ Error calculating success rate: {e}")

    st.subheader("Step 2: Price & Competition Check")

    try:
        if price_col:
            # Handle invalid or missing price data
            invalid_price_rows = df[df[price_col].isnull()]
            if not invalid_price_rows.empty:
                st.warning(f"⚠️ There are {invalid_price_rows.shape[0]} rows with invalid or missing prices.")

            avg_price = round(df[price_col].mean(), 2)
            st.write(f"💰 Average Price: **${avg_price}**")

            if avg_price <= 100:
                st.success("✅ Price is in a good range.")
            else:
                st.warning("⚠️ Price might be a bit high.")
        else:
            st.error("❌ Price data is invalid or missing.")

        # Calculate average reviews
        avg_reviews = round(df["Reviews"].mean(), 0) if "Reviews" in df.columns else None
        if avg_reviews is not None:
            st.write(f"⭐ Average Reviews: **{avg_reviews}**")
            if avg_reviews <= 300:
                st.success("✅ Competition is manageable.")
            else:
                st.info("ℹ️ High review count — might be competitive.")
        else:
            st.error("❌ Reviews data is invalid or missing.")

    except Exception as e:
        st.error(f"❌ Error analyzing price or reviews: {e}")
