import streamlit as st
import pandas as pd

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

# Option to choose between single file upload and compare two files
compare_two_files = st.radio("Choose the mode", ("Single Product Analysis", "Compare 2 Products"))

def get_most_common_product_name(df):
    # Search for columns that might contain the product name (assuming it's likely in 'Product', 'Name', or 'Title')
    possible_columns = ['product', 'name', 'title']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in possible_columns):
            # If a relevant column is found, return the most common value
            most_common_name = df[col].mode()[0]  # Get the most frequent value
            return most_common_name
    return "Unknown Product"  # Default if no common product name is found

if compare_two_files == "Single Product Analysis":
    uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # 🔍 Get the most common product name
        product_name = get_most_common_product_name(df)
        st.write(f"Product Name: **{product_name}**")

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

            # 📈 Revenue calculations
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

            # Calculate average reviewsimport streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

def clean_product_name(product_details):
    # Remove unwanted characters and extra spaces
    product_details = re.sub(r"[^a-zA-Z0-9\s]", "", product_details)  # Keep only alphanumeric characters and spaces
    product_details = ' '.join(product_details.split())  # Remove extra spaces
    return product_details.strip()

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

    # Product Name Extraction (Simplified Version)
    product_name = ""
    if 'Product Details' in df.columns:
        # Take the first row from the Product Details column
        product_name = df['Product Details'].iloc[0]
        product_name = clean_product_name(product_name)

    st.subheader("Product Analysis")

    # Removed the part where product name is displayed
    # Now the product name won't be shown on the screen

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

        # 📈 Revenue calculations
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
