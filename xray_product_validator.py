import streamlit as st
import pandas as pd
import urllib.parse
import re
from collections import Counter

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

# Toggle for comparison mode
compare_mode = st.checkbox("Compare 2 Products/Files")

def clean_product_details(product_details):
    # Clean up product details, remove special characters and excessive whitespace
    product_details = re.sub(r'[^a-zA-Z0-9\s]', '', product_details)
    product_details = re.sub(r'\s+', ' ', product_details).strip()
    return product_details

def extract_product_name(df):
    # Find the Product Details column
    if "Product Details" in df.columns:
        # Get all product descriptions in the "Product Details" column
        product_details = df["Product Details"].dropna().astype(str)
        words = ' '.join(product_details).split()

        # Find the most common words
        word_counts = Counter(words)
        common_words = word_counts.most_common(5)  # Get the 5 most common words

        # The product name will likely be a combination of the most common and meaningful words
        product_name = ' '.join([word[0] for word in common_words]).title()
        return product_name
    else:
        return None

def process_file(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # Rename Reviews column
    for col in df.columns:
        if "review" in col.lower() and "count" in col.lower():
            df.rename(columns={col: "Reviews"}, inplace=True)
            break

    # Get Revenue column
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

    # Get Price column
    price_col = None
    for col in df.columns:
        if "price" in col.lower():
            price_col = col
            break

    # Clean up data
    if revenue_col:
        df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

    if price_col:
        df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

    if "Reviews" in df.columns:
        df["Reviews"] = df["Reviews"].replace({',': ''}, regex=True)
        df["Reviews"] = pd.to_numeric(df["Reviews"], errors='coerce')

    return df, revenue_col, price_col

def analyze_and_display(df, revenue_col, price_col, label="Product"):
    st.markdown(f"### 📊 {label} Analysis")

    try:
        total_sellers = df.shape[0]
        sellers_above_10k = df[df[revenue_col] > 10000].shape[0]
        success_rate = round((sellers_above_10k / total_sellers) * 100, 2)

        st.write(f"✅ Success Rate: **{success_rate}%** ({sellers_above_10k} out of {total_sellers} sellers over $10K revenue)")

        if success_rate >= 75:
            st.success("🎯 This product has a high success rate!")
        else:
            st.warning("⚠️ This product might not have a high enough success rate.")

        # Revenue
        total_revenue = df[revenue_col].sum()
        avg_revenue = round(total_revenue / total_sellers, 2)
        st.write(f"📈 Average Revenue per Seller: **${avg_revenue:,}**")
        st.write(f"💵 Total Revenue: **${total_revenue:,.2f}**")
        st.write(f"👥 # of Sellers: **{total_sellers}**")

    except Exception as e:
        st.error(f"❌ Error calculating success rate or revenue: {e}")

    try:
        if price_col:
            avg_price = round(df[price_col].mean(), 2)
            st.write(f"💰 Average Price: **${avg_price}**")

            if avg_price <= 100:
                st.success("✅ Price is in a good range.")
            else:
                st.warning("⚠️ Price might be a bit high.")
        else:
            st.error("❌ Price data is invalid or missing.")

        if "Reviews" in df.columns:
            avg_reviews = round(df["Reviews"].mean(), 0)
            st.write(f"⭐ Average Reviews: **{avg_reviews}**")

            if avg_reviews <= 300:
                st.success("✅ Competition is manageable.")
            else:
                st.info("ℹ️ High review count — might be competitive.")
        else:
            st.error("❌ Reviews data is invalid or missing.")
    except Exception as e:
        st.error(f"❌ Error analyzing price or reviews: {e}")

    # 🛒 Smart Alibaba button
    product_name = extract_product_name(df)
    if product_name:
        search_query = urllib.parse.quote_plus(product_name)
        alibaba_url = f"https://www.alibaba.com/trade/search?SearchText={search_query}"
        st.markdown(f"[🔍 Find Suppliers on Alibaba]({alibaba_url})", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not determine a product name for Alibaba search.")

# ---- DEFAULT SINGLE FILE MODE ----
if not compare_mode:
    uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")
    if uploaded_file is not None:
        df, revenue_col, price_col = process_file(uploaded_file)
        analyze_and_display(df, revenue_col, price_col)

# ---- COMPARE MODE ----
else:
    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader("Upload File 1", type="csv", key="file1")
    with col2:
        file2 = st.file_uploader("Upload File 2", type="csv", key="file2")

    if file1 and file2:
        with col1:
            df1, revenue1, price1 = process_file(file1)
            analyze_and_display(df1, revenue1, price1, label="Product 1")

        with col2:
            df2, revenue2, price2 = process_file(file2)
            analyze_and_display(df2, revenue2, price2, label="Product 2")
