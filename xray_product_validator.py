import streamlit as st
import pandas as pd

st.set_page_config(page_title="Xray Product Validator")
st.title("🔍 Xray Product Validator")

# Button to enable the comparison mode
compare_mode = st.button("Compare 2 Products/Files")

# Function to analyze the data for each file
def analyze_file(uploaded_file):
    result = {}
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

        # Clean up the revenue and price columns
        if revenue_col:
            df[revenue_col] = df[revenue_col].replace({',': '', '$': ''}, regex=True)
            df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

        if price_col:
            df[price_col] = df[price_col].replace({',': '', '$': ''}, regex=True)
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce')

        # Success rate calculations
        try:
            total_sellers = df.shape[0]
            sellers_above_10k = df[df[revenue_col] > 10000].shape[0]
            success_rate = round((sellers_above_10k / total_sellers) * 100, 2)

            total_revenue = df[revenue_col].sum()
            avg_revenue = round(total_revenue / total_sellers, 2)

            result = {
                "Success Rate": f"{success_rate}% ({sellers_above_10k}/{total_sellers})",
                "Average Revenue per Seller": f"${avg_revenue:,.2f}",
                "Total Revenue": f"${total_revenue:,.2f}",
                "# of Sellers": total_sellers,
                "Average Price": f"${df[price_col].mean():,.2f}" if price_col else "N/A",
                "Average Reviews": f"{df['Reviews'].mean():,.0f}" if 'Reviews' in df.columns else "N/A"
            }
        except Exception as e:
            st.error(f"❌ Error calculating success rate or revenue: {e}")

    return result

# Default mode: single file upload
if not compare_mode:
    uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")
    if uploaded_file is not None:
        results = analyze_file(uploaded_file)
        st.markdown("### ✅ Product Analysis")
        for key, val in results.items():
            st.write(f"**{key}:** {val}")

# Compare mode: side-by-side file uploads
else:
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
