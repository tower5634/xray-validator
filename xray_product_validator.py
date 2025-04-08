import streamlit as st
import pandas as pd
import os
import urllib.parse

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

compare_mode = st.checkbox("Compare 2 products/files")

if not compare_mode:
    uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

    if uploaded_file is not None:
        # Extract product keyword from filename
        file_name = uploaded_file.name
        product_keyword = file_name.split("_")[0] if "_" in file_name else os.path.splitext(file_name)[0]

        alibaba_url = f"https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&SearchText={urllib.parse.quote(product_keyword)}"

        if st.button("🔎 Find Suppliers on Alibaba"):
            st.markdown(f"[Click here to search '{product_keyword}' on Alibaba]({alibaba_url})", unsafe_allow_html=True)

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

        st.subheader("Success Rate")

        # Clean up the revenue and price columns
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

            st.write(f"📈 Average Revenue per Seller: **${avg_revenue:,}**")
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

else:
    st.write("🔄 Compare two Xray CSV files side by side")

    file1 = st.file_uploader("Upload first Xray CSV file", type="csv", key="file1")
    file2 = st.file_uploader("Upload second Xray CSV file", type="csv", key="file2")

    def analyze_file(file, label):
        result = {}
        try:
            df = pd.read_csv(file)

            for col in df.columns:
                if "review" in col.lower() and "count" in col.lower():
                    df.rename(columns={col: "Reviews"}, inplace=True)
                    break

            revenue_col = next((col for col in df.columns if "revenue" in col.lower()), None)
            price_col = next((col for col in df.columns if "price" in col.lower()), None)

            if revenue_col:
                df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

            if price_col:
                df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)
                df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

            if "Reviews" in df.columns:
                df["Reviews"] = df["Reviews"].replace({',': ''}, regex=True)
                df["Reviews"] = pd.to_numeric(df["Reviews"], errors='coerce')

            total_sellers = df.shape[0]
            sellers_above_10k = df[df[revenue_col] > 10000].shape[0]
            success_rate = round((sellers_above_10k / total_sellers) * 100, 2)
            total_revenue = df[revenue_col].sum()
            avg_revenue = round(total_revenue / total_sellers, 2)
            avg_price = round(df[price_col].mean(), 2)
            avg_reviews = round(df["Reviews"].mean(), 0) if "Reviews" in df.columns else None

            result = {
                "Success Rate": f"{success_rate}%",
                "Avg Revenue/Seller": f"${avg_revenue:,}",
                "Total Revenue": f"${total_revenue:,.2f}",
                "Avg Price": f"${avg_price}",
                "Avg Reviews": f"{avg_reviews}" if avg_reviews is not None else "N/A",
                "Sellers": total_sellers
            }
        except Exception as e:
            result = {"Error": str(e)}

        return result

    if file1 and file2:
        col1, col2 = st.columns(2)

        with col1:
            st.write("📊 **First Product Analysis**")
            result1 = analyze_file(file1, "File 1")
            for k, v in result1.items():
                st.write(f"{k}: {v}")

        with col2:
            st.write("📊 **Second Product Analysis**")
            result2 = analyze_file(file2, "File 2")
            for k, v in result2.items():
                st.write(f"{k}: {v}")
