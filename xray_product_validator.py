import streamlit as st
import pandas as pd
import re
import os
import requests
from dotenv import load_dotenv

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

load_dotenv()

uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

def clean_product_name(product_details):
    product_details = re.sub(r"[^a-zA-Z0-9\s]", "", product_details)
    product_details = ' '.join(product_details.split())
    return product_details.strip()

def check_patent_status(product_name):
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    if not serpapi_api_key:
        return {
            "status": "Error",
            "confidence": 0,
            "details": "SerpApi API key not found. Please set it in the .env file."
        }

    cleaned_name = re.sub(r"[^a-zA-Z0-9\s]", "", product_name).strip()

    params = {
        "engine": "google_patents",
        "q": cleaned_name,
        "api_key": serpapi_api_key
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()

        if "organic_results" in data and data["organic_results"]:
            first_result = data["organic_results"][0]
            patent_title = first_result.get("title", "N/A")
            patent_link = first_result.get("link", "N/A")
            snippet = first_result.get("snippet", "N/A")

            return {
                "status": "Patented",
                "confidence": 95,
                "details": f"Patent Title: {patent_title}\nLink: {patent_link}\nSnippet: {snippet}"
            }
        else:
            return {
                "status": "No Patents Found",
                "confidence": 90,
                "details": "No patents were found related to the product name."
            }

    except requests.RequestException as e:
        return {
            "status": "Error",
            "confidence": 0,
            "details": f"An error occurred while querying SerpApi: {e}"
        }

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        for col in df.columns:
            if "review" in col.lower() and "count" in col.lower():
                df.rename(columns={col: "Reviews"}, inplace=True)
                break

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

        price_col = None
        for col in df.columns:
            if "price" in col.lower():
                price_col = col
                break

        product_name = ""
        if 'Product Details' in df.columns:
            product_name = df['Product Details'].iloc[0]
            product_name = clean_product_name(product_name)

        st.subheader("Product Analysis")

        if revenue_col:
            df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)
            df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

        if price_col:
            df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

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

        st.write(f"📈 Average Revenue per Seller: **${avg_revenue:,}**")
        st.write(f"💵 Total Revenue: **${total_revenue:,.2f}**")
        st.write(f"👥 # of Sellers: **{total_sellers}**")

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

        st.button("Find Suppliers on Alibaba", 
                  on_click=lambda: st.write(f"Click to find product: https://www.alibaba.com/search?q={product_name.replace(' ', '+')}"))

        if product_name:
            st.subheader("🛡️ Patent Check")

            patent_result = check_patent_status(product_name)

            st.write(f"🔎 Patent Status: **{patent_result['status']}**")
            st.write(f"📊 Confidence: **{patent_result['confidence']}%**")
            st.write(f"🧠 Details: {patent_result['details']}")

            if patent_result['status'] == "Patented":
                st.error("🚫 This product appears to be patented. Proceed with caution.")
            elif patent_result['status'] == "No Patents Found":
                st.success("✅ No related patents found. Product may be safe to proceed.")
            else:
                st.warning("⚠️ Unable to determine patent status. Please review manually.")

    except Exception as e:
        st.error(f"❌ Error reading CSV or processing data: {e}")
