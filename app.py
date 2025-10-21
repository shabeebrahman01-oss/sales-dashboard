import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import gdown

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("📊 Sales Analytics Dashboard")
st.markdown("### Visualize and analyze your sales data interactively")

# Sidebar
st.sidebar.header("🔧 Configuration")

# Data source selection
data_source = st.sidebar.radio(
    "Select Data Source:",
    ["Upload CSV File", "Load from Google Drive"]
)

df = None

if data_source == "Upload CSV File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload your sales CSV file", 
        type=['csv', 'xlsx']
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.sidebar.success("✅ File loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading file: {e}")

elif data_source == "Load from Google Drive":
    st.sidebar.markdown("**Enter Google Drive File ID:**")
    st.sidebar.info("Extract the file ID from your shareable link")
    
    file_id = st.sidebar.text_input("File ID:", placeholder="1ABC123xyz456")
    
    if st.sidebar.button("Load Data"):
        if file_id:
            try:
                with st.spinner("Downloading from Google Drive..."):
                    url = f"https://drive.google.com/uc?id={file_id}"
                    output = 'temp_sales_data.csv'
                    gdown.download(url, output, quiet=False)
                    df = pd.read_csv(output)
                st.sidebar.success("✅ Data loaded from Google Drive!")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        else:
            st.sidebar.warning("Please enter a File ID")

# Main content
if df is not None:
    # Convert date column if exists
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    if date_columns:
        df[date_columns[0]] = pd.to_datetime(df[date_columns[0]], errors='coerce')
    
    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Filters")
    
    # Show raw data option
    show_raw = st.sidebar.checkbox("Show Raw Data", value=False)
    
    # Column selection for filtering
    if len(df.columns) > 0:
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            filter_col = st.sidebar.selectbox("Filter by column:", ["None"] + categorical_cols)
            if filter_col != "None":
                unique_values = df[filter_col].unique()
                selected_values = st.sidebar.multiselect(
                    f"Select {filter_col}:",
                    options=unique_values,
                    default=unique_values
                )
                df = df[df[filter_col].isin(selected_values)]
    
    # Display raw data
    if show_raw:
        st.subheader("📋 Raw Data")
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Rows:** {len(df)} | **Total Columns:** {len(df.columns)}")
    
    # Key metrics
    st.markdown("---")
    st.subheader("📈 Key Metrics")
    
    # Try to find sales column
    sales_col = None
    for col in df.columns:
        if 'sales' in col.lower() or 'revenue' in col.lower() or 'amount' in col.lower():
            sales_col = col
            break
    
    if sales_col:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = df[sales_col].sum()
            st.metric("💰 Total Sales", f"${total_sales:,.2f}")
        
        with col2:
            avg_sales = df[sales_col].mean()
            st.metric("📊 Average Sale", f"${avg_sales:,.2f}")
        
        with col3:
            total_transactions = len(df)
            st.metric("🛒 Total Transactions", f"{total_transactions:,}")
        
        with col4:
            # Find product/category column
            product_col = None
            for col in df.columns:
                if 'product' in col.lower() or 'category' in col.lower() or 'item' in col.lower():
                    product_col = col
                    break
            if product_col:
                unique_products = df[product_col].nunique()
                st.metric("📦 Unique Products", f"{unique_products:,}")
    
    # Visualizations
    st.markdown("---")
    st.subheader("📊 Data Visualizations")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Distribution", "🥧 Breakdown", "🔥 Heatmap"])
    
    with tab1:
        st.markdown("#### Sales Trends")
        if date_columns and sales_col:
            date_col = date_columns[0]
            trend_df = df.groupby(date_col)[sales_col].sum().reset_index()
            fig1 = px.line(trend_df, x=date_col, y=sales_col,
                          title='Sales Over Time',
                          markers=True)
            fig1.update_layout(hovermode='x unified')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Date column not found for trend analysis")
        
        # Product sales trend
        if product_col and sales_col:
            col1, col2 = st.columns(2)
            with col1:
                top_n = st.slider("Show top N products:", 5, 20, 10)
            
            product_sales = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False).head(top_n).reset_index()
            fig2 = px.bar(product_sales, x=product_col, y=sales_col,
                         title=f'Top {top_n} Products by Sales',
                         color=sales_col,
                         color_continuous_scale='Blues')
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("#### Sales Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            if sales_col:
                fig3 = px.histogram(df, x=sales_col, 
                                   title='Sales Distribution',
                                   nbins=30,
                                   color_discrete_sequence=['#636EFA'])
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            if sales_col:
                fig4 = px.box(df, y=sales_col,
                             title='Sales Box Plot',
                             color_discrete_sequence=['#EF553B'])
                st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        st.markdown("#### Category Breakdown")
        
        if product_col and sales_col:
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                pie_data = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False).head(8)
                fig5 = px.pie(values=pie_data.values, names=pie_data.index,
                             title='Sales Share by Product (Top 8)',
                             hole=0.4)
                st.plotly_chart(fig5, use_container_width=True)
            
            with col2:
                # Treemap
                treemap_data = df.groupby(product_col)[sales_col].sum().reset_index().head(10)
                fig6 = px.treemap(treemap_data, path=[product_col], values=sales_col,
                                 title='Sales Treemap (Top 10)',
                                 color=sales_col,
                                 color_continuous_scale='RdYlGn')
                st.plotly_chart(fig6, use_container_width=True)
    
    with tab4:
        st.markdown("#### Correlation Heatmap")
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            fig7 = px.imshow(corr_matrix,
                            title='Correlation Matrix',
                            color_continuous_scale='RdBu',
                            aspect='auto',
                            text_auto='.2f')
            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("Not enough numeric columns for correlation analysis")
    
    # Download section
    st.markdown("---")
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f'sales_data_filtered_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )
    
    with col2:
        # Summary statistics
        if sales_col:
            summary = df[sales_col].describe().to_frame()
            csv_summary = summary.to_csv().encode('utf-8')
            st.download_button(
                label="📊 Download Summary Statistics",
                data=csv_summary,
                file_name='sales_summary.csv',
                mime='text/csv'
            )

else:
    # Welcome screen
    st.info("👆 Please upload a file or load data from Google Drive to begin")
    
    st.markdown("""
    ### 📋 Getting Started
    
    **Option 1: Upload File**
    - Upload your CSV or Excel file using the sidebar
    
    **Option 2: Load from Google Drive**
    1. Share your file on Google Drive
    2. Get the shareable link
    3. Extract the File ID (part between `/d/` and `/view`)
    4. Enter the File ID in the sidebar
    
    ### 📊 Expected Data Format
    Your file should contain columns such as:
    - **Date** - Transaction date
    - **Sales/Revenue/Amount** - Sales value
    - **Product/Category** - Product name or category
    - **Region** - Geographic region (optional)
    - **Quantity** - Number of units sold (optional)
    - **Customer** - Customer information (optional)
    
    ### 🎯 Dashboard Features
    - 📈 Interactive sales trends and visualizations
    - 📊 Key metrics and KPIs
    - 🔍 Dynamic filtering
    - 💾 Export filtered data
    - 🎨 Multiple chart types
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | Data from Google Drive → Colab → GitHub → Streamlit")
