import streamlit as st
import pandas as pd
import re
from collections import Counter

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

def extract_main_product_name(product_names):
    words = []
    for name in product_names:
        tokens = re.findall(r'\b\w+\b', str(name).lower())
        words.extend(tokens)

    common_words = [word for word in words if word not in {
        "the", "and", "for", "with", "a", "of", "to", "in", "on", "by",
        "an", "or", "is", "at", "from", "this", "that", "it", "as", "be",
        "ultrasafe", "pack", "portable", "charger", "jumper", "box",
        "engine", "engines", "starter", "boost", "plus", "battery", "jump",
        "cables", "gasoline", "diesel", "noco", "gb40", "1000a", "12v"
    }]

    most_common = Counter(common_words).most_common(5)
    return " ".join([word for word, _ in most_common])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # 🔍 Identify important columns
    for col in df.columns:
        if "review" in col.lower() and "count" in col.lower():
            df.rename(columns={col: "Reviews"}, inplace=True)
            break

    revenue_col = next((col for col in df.columns if "revenue" in col.lower() and "parent" in col.lower()), None)
    if not revenue_col:
        revenue_col = next((col for col in df.columns if "revenue" in col.lower()), None)

    price_col = next((col for col in df.columns if "price" in col.lower()), None)

    # 🔍 Automatically detect product name
    product_name = ""
    if "Product Details" in df.columns:
        product_name = extract_main_product_name(df["Product Details"].dropna().head(20))
        if product_name:
            search_url = f"https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={product_name.replace(' ', '+')}"
            if st.button("🔎 Find Suppliers on Alibaba"):
                st.markdown(f"[Click here to search on Alibaba for '{product_name}']({search_url})", unsafe_allow_html=True)

    st.subheader("Success Rate")

    # Clean revenue and price
    if revenue_col:
        df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

    if price_col:
        df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

    try:
        total_sellers = df.shape[0]
        sellers_above_10k = df[df[revenue_col] > 10000].shape[0]
        success_rate = round((sellers_above_10k / total_sellers) * 100, 2)

        st.write(f"✅ Success Rate: **{success_rate}%** ({sellers_above_10k} out of {total_sellers} sellers over $10K revenue)")

        if success_rate >= 75:
            st.success("🎯 This product has a high success rate!")
        else:
            st.warning("⚠️ This product might not have a high enough success rate.")

        total_revenue = df[revenue_col].sum()
        avg_revenue = round(total_revenue / total_sellers, 2)

        st.write(f"📈 Average Revenue per Seller: **${avg_revenue:,.2f}**")
        st.write(f"💵 Total Revenue: **${total_revenue:,.2f}**")
        st.write(f"👥 # of Sellers: **{total_sellers}**")

    except Exception as e:
        st.error(f"❌ Error calculating success rate or revenue: {e}")

    st.subheader("Price & Competition Check")

    try:
        if price_col:
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

        if "Reviews" in df.columns:
            df["Reviews"] = df["Reviews"].replace({',': ''}, regex=True)
            df["Reviews"] = pd.to_numeric(df["Reviews"], errors='coerce')
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
