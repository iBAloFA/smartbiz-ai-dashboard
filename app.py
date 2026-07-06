import streamlit as st
import pandas as pd
import plotly.express as px
import google.genai as genai
import os

# 1. Page Configuration & Elite Styling
st.set_page_config(page_title="SmartBiz AI Dashboard", page_icon="📊", layout="wide")

# Custom UI styling injection for clean card containers
st.markdown("""
    <style>
    .main-title { font-size: 36px; font-weight: bold; color: #1E3A8A; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #6B7280; margin-bottom: 25px; }
    .kpi-card {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        color: white;
        margin-bottom: 15px;
    }
    .kpi-title { font-size: 14px; color: #94A3B8; font-weight: 500; }
    .kpi-value { font-size: 26px; font-weight: bold; color: #F8FAFC; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 SmartBiz AI Insights Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Turn raw spreadsheets into winning business decisions instantly. Aligned with UN SDG Goal 8.</div>', unsafe_allow_html=True)

# 2. Key Management Setup
try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.info("💡 Google Gemini API Key required for analysis features.")
    api_key = st.text_input("Enter Free Gemini API Key:", type="password")

# 3. File Upload Interface
uploaded_file = st.file_uploader("Upload your sales or revenue CSV file here:", type=["csv"])

if uploaded_file is not None:
    # Read the dataset
    df = pd.read_csv(uploaded_file)
    
    # Try to clean column names to avoid matching errors
    df.columns = df.columns.str.strip()
    
    # --- STEP 4: ADD HIGH-VALUE KPI CARDS ---
    st.markdown("### 🔑 Performance Highlights")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    # Simple automated checks to guess metrics columns (Sales, Profit, etc.)
    sales_col = next((c for c in df.columns if 'sale' in c.lower() or 'revenue' in c.lower()), None)
    profit_col = next((c for c in df.columns if 'profit' in c.lower() or 'gain' in c.lower()), None)
    
    total_transactions = f"{len(df):,}"
    total_sales_val = f"${df[sales_col].sum():,.2f}" if sales_col else "N/A"
    total_profit_val = f"${df[profit_col].sum():,.2f}" if profit_col else "N/A"
    
    with kpi_col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">TOTAL DATA RECORDS</div><div class="kpi-value">{total_transactions}</div></div>', unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GROSS TRACKED REVENUE</div><div class="kpi-value">{total_sales_val}</div></div>', unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">NET OPERATIONAL PROFIT</div><div class="kpi-value">{total_profit_val}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 5. Main Layout Split View
    col1, col2 = st.columns([4, 5])
    
    with col1:
        st.markdown("### 📋 Uploaded Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
    with col2:
        st.markdown("### 📈 Interactive Visual Trends")
        columns = df.columns.tolist()
        
        # User dropdown adjustments
        x_axis = st.selectbox("Choose Category / X-Axis:", columns, index=min(len(columns)-1, 10))
        y_axis = st.selectbox("Choose Numeric Values / Y-Axis:", columns, index=min(1, len(columns)-1))
        
        try:
            # FIX: Group rows together and sort so charts don't look crowded
            chart_df = df.groupby(x_axis)[y_axis].sum().reset_index()
            chart_df = chart_df.sort_values(by=y_axis, ascending=False).head(10) # Grab top 10 categories
            
            # Render polished chart vertical bars
            fig = px.bar(
                chart_df, 
                x=x_axis, 
                y=y_axis, 
                title=f"Top 10: Total {y_axis} by {x_axis}", 
                template="plotly_dark", # Matches sleek dark designs
                color=y_axis,
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not group chart axes. Please pick a category name for X-axis and a number for Y-axis.")

    st.markdown("---")
    
    # 6. Strategic AI Dashboard Execution Engine
    st.markdown("### 🤖 Strategic Executive Analysis")
    if st.button("🚀 Generate AI CFO Turnaround Strategy"):
        if not api_key:
            st.error("Please add your Gemini API Key above to activate the strategic adviser panel.")
        else:
            with st.spinner("Processing raw transaction matrices using Google Gemini..."):
                try:
                    # Provide an optimized short dataset description to protect system memory
                    data_summary = df.describe(include='all').to_string()
                    
                    client = genai.Client(api_key=api_key)
                    
                    prompt_instructions = (
                        "You are an elite, sharp, and highly strategic Chief Financial Officer (CFO) "
                        "and business turnaround consultant. Your tone is professional, urgent, "
                        "and fiercely protective of profit margins.\n\n"
                        "Analyze the provided business statistics. Skip all generic introductions or pleasantries. "
                        "Provide exactly three bulleted, razor-sharp recommendations.\n\n"
                        "Each point must follow this strict format:\n"
                        "1. 📈 [OBSERVATION]: Explain exactly what metric looks dangerous or weak in their data.\n"
                        "2. 💡 [ACTION STEP]: Provide a concrete financial strategy to fix it today.\n"
                        "3. 💰 [EXPECTED IMPACT]: Give a realistic percentage or cost-cutting projection of what they stand to save.\n\n"
                        f"Here is our raw business dashboard matrix data:\n{data_summary}"
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_instructions,
                    )
                    
                    # Styled output call block
                    st.info("### AI CFO Consulting Output (Powered by Gemini)")
                    st.markdown(response.text)
                    
                except Exception as ex:
                    st.error(f"API Error encountered: {ex}")
