
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Xray Product Validator", layout="centered")

st.title("🔍 Helium 10 Xray Product Validator")
st.markdown("Upload a Helium 10 Xray CSV export to analyze product potential.")

uploaded_file = st.file_uploader("Upload your Xray CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # ✅ NEW: Auto-rename the Reviews column
    for col in df.columns:
        if "review" in col.lower() and "count" in col.lower():
            df.rename(columns={col: "Reviews"}, inplace=True)
            break
        for col in df.columns:
    if "review" in col.lower() and "count" in col.lower():
        df.rename(columns={col: "Reviews"}, inplace=True)
        break

    try:
        df["Parent Level Revenue"] = df["Parent Level Revenue"].replace('[\$,]', '', regex=True).astype(float)
        df["Price  $"] = df["Price  $"].replace('[\$,]', '', regex=True).astype(float)
        df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce")

        total_sellers = len(df)
        successful_sellers = df[df["Parent Level Revenue"] > 10000]
        success_rate = round(len(successful_sellers) / total_sellers * 100, 2)
        avg_price = round(df["Price  $"].mean(), 2)
        avg_reviews = int(df["Reviews"].mean())

        top_keywords = (
            successful_sellers["Product Details"]
            .astype(str)
            .str.lower()
            .str.split()
            .explode()
            .value_counts()
            .head(10)
            .to_dict()
        )

        competition = "High" if avg_reviews > 500 or total_sellers > 20 else "Low"
        decision = "GO ✅" if success_rate >= 75 and avg_price < 100 else "NO GO ❌"

        st.subheader("📊 Analysis Results")
        st.markdown(f"**Success Rate:** {success_rate}%")
        st.markdown(f"**Average Price:** ${avg_price}")
        st.markdown(f"**Total Sellers:** {total_sellers}")
        st.markdown(f"**Average Reviews:** {avg_reviews}")
        st.markdown(f"**Competition Level:** {competition}")
        st.markdown(f"**Final Verdict:** {decision}")

        st.subheader("🔑 Top Variant Keywords")
        for word, count in top_keywords.items():
            st.markdown(f"- **{word}**: {count} mentions")

        st.caption("⚠️ This tool is not affiliated with or endorsed by Helium 10. Data is used for personal analysis only.")

    except Exception as e:
        st.error(f"Something went wrong while processing your file: {e}")
