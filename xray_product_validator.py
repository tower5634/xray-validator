import streamlit as st
import pandas as pd

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

# Add a button for comparing two files
compare_mode = st.button("Compare 2 Products/Files")

# Function to analyze the data for each file
def analyze_file(uploaded_file):
    result = {}
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Identify and rename reviews column
        for col in df.columns:
            if "review" in col.lower() and "count" in col.lower():
                df.rename(columns={col: "Reviews"}, inplace=True)
                break

        # Identify revenue column
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

        # Identify price column
        price_col = None
        for col in df.columns:
            if "price" in col.lower():
                price_col = col
                break

        # Clean revenue
        if revenue_col:
            df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)
            df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

        # Clean price
        if price_col:
            df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

        # Clean reviews
        if "Reviews" in df.columns:
            df["Reviews"] = df["Reviews"].replace({',': ''}, regex=True)
            df["Reviews"] = pd.to_numeric(df["Reviews"], errors='coerce')

        # Metrics
        total_sellers = df.shape[0]
        sellers_above_10k = df[df[revenue_col] > 10000].shape[0]
        success_rate = round((sellers_above_10k / total_sellers) * 100, 2)

        total_revenue = df[revenue_col].sum()
        avg_revenue = round(total_revenue / total_sellers, 2)
        avg_price = round(df[price_col].mean(), 2) if price_col else None
        avg_reviews = round(df["Reviews"].mean(), 0) if "Reviews" in df.columns else None

        result = {
            "Success Rate": f"{success_rate}% ({sellers_above_10k}/{total_sellers})",
            "Average Revenue per Seller": f"${avg_revenue:,.2f}",
            "Total Revenue": f"${total_revenue:,.2f}",
            "# of Sellers": total_sellers,
            "Average Price": f"${avg_price}" if avg_price is not None else "N/A",
            "Average Reviews": int(avg_reviews) if avg_reviews is not None else "N/A"
        }
    return result

# If in compare mode, show file uploaders for 2 products
if compare_mode:
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload CSV for Product 1", type="csv", key="file1")
    with col2:
        file2 = st.file_uploader("Upload CSV for Product 2", type="csv", key="file2")

    if file1 and file2:
        results1 = analyze_file(file1)
        results2 = analyze_file(file2)

        st.markdown("### 📊 Side-by-Side Comparison")
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📦 Product 1")
                for key, val in results1.items():
                    st.write(f"**{key}:** {val}")
            with col2:
                st.subheader("📦 Product 2")
                for key, val in results2.items():
                    st.write(f"**{key}:** {val}")
else:
    # Default mode: single file upload
    uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")
    if uploaded_file is not None:
        results = analyze_file(uploaded_file)
        st.markdown("### ✅ Product Analysis")
        for key, val in results.items():
            st.write(f"**{key}:** {val}")
