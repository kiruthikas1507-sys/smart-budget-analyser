import streamlit as st
import pandas as pd
st.markdown("""
    <style>
    /* 1. Background and Text Color Force */
    .stApp {
        background-color: white !important;
    }

    /* 2. Button Text Visibility - Force WHITE */
    button p, .stButton > button {
        color: white !important;
        font-weight: bold !important;
    }

    /* 3. Input Labels and Normal Text - Force BLACK */
    label, p, span, h1, h2, h3, .stMarkdown {
        color: black !important;
    }

    /* 4. Input Box Text - Force BLACK */
    input, textarea {
        color: black !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: black !important;
    }

    /* 5. Sidebar Text Fix */
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. GLOBAL VISIBILITY & CSS (Force Light Mode) ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; color: black !important; }
    input, textarea { color: black !important; background-color: #f0f2f6 !important; }
    label, p, span, h1, h2, h3 { color: black !important; }
    
    /* Sidebar styling for vertical menu */
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    
    /* Blue Glow Button for Analyze */
    div.stButton > button {
        background-color: #111 !important; color: white !important;
        border-radius: 30px; transition: all 0.4s ease; width: 100%;
    }
    div.stButton > button:hover {
        color: #FFFFFF !important;
        border-color: #00d2ff !important;
        box-shadow: 0 0 10px #00d2ff, 0 0 30px #00d2ff;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CATEGORIZATION LOGIC ---
def categorize_expense(description):
    desc = description.lower()
    if any(word in desc for word in ['food', 'swiggy', 'tea','lunch']): return '🍔 Food'
    elif any(word in desc for word in ['petrol', 'uber', 'bus']): return '🚗 Travel'
    elif any(word in desc for word in ['rent', 'room']): return '🏠 Housing'
    elif any(word in desc for word in ['amazon', 'shopping']): return '🛍️ Shopping'
    elif any(word in desc for word in ['bill', 'eb', 'recharge']): return '⚡ Bills'
    else: return '📦 General'


# --- 3. SESSION STATE FOR LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "123"}    

# --- 4. SIGN IN / LOGIN PAGE ---
if not st.session_state.logged_in:
    st.title("🔐 Sign In - Smart Budget AI")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if user in st.session_state.user_db and st.session_state.user_db[user] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Invalid Credentials")
    with col2:
        #if st.button("Sign Up"):#
            #st.info("Sign Up feature coming soon! Use admin/123 for now.")#
        if st.button("Sign Up"):
            if user and password:
               st.session_state.user_db[user] = password
               st.success("Account Created! Now Login.")
            else:
                st.error("Enter Username and Password")   

# --- 5. MAIN APP PAGE (Vertical Slides) ---
else:
    # Sidebar Vertical Menu
    if 'page_index' not in st.session_state:st.session_state.page_index=0
    with st.sidebar:
        st.header("🏠 Menu")
        # Vertical Slide Selection
        page = st.radio("Go to:", ["📝 Input Data", "📊 Insights", "📋 Summary Table", "📈 Spending Graph"],index=st.session_state.page_index)
        st.divider()
        lang = st.selectbox("🌐 Language", ["English", "Tamil"])
        user_budget = st.number_input("Monthly Budget", min_value=100, value=5000)
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # --- PAGE 1: INPUT DATA ---
    if page == "📝 Input Data":
        st.title("📝 Enter Expenses")
        user_input = st.text_area("Enter (Item, Price):", placeholder="Lunch, 150\nPetrol, 500", height=200)
        if st.button("Analyze"):
            if user_input.strip():
                data = []
                for line in user_input.strip().split('\n'):
                    if ',' in line:
                        parts = line.split(',')
                        data.append([parts[0].strip(), float(parts[1].strip()), categorize_expense(parts[0])])
                st.session_state.temp_data = data
                st.session_state.page_index=1 
                st.rerun()
                st.success("Data analyzed! Check other pages from sidebar.")

    # Data check logic
    if 'temp_data' in st.session_state and st.session_state.temp_data:
        df = pd.DataFrame(st.session_state.temp_data, columns=['Description', 'Amount', 'Category'])
        total_spent = df['Amount'].sum()
        usage = (total_spent / user_budget) * 100

        # --- PAGE 2: INSIGHTS ---
        if page == "📊 Insights":
            st.title("📊 Financial Insights")
            col1, col2 = st.columns(2)
            col1.metric("Total Spent", f"₹{total_spent:,.2f}")
            col2.metric("Budget Usage", f"{usage:.1f}%")
            st.progress(min(usage / 100, 1.0))
            if total_spent > user_budget: st.warning("⚠️ Budget Exceeded!")
            else: st.success("✅ Within Budget Limit")

        # --- PAGE 3: SUMMARY TABLE ---
        elif page == "📋 Summary Table":
            st.title("📋 Expense Summary")
            st.table(df)

        # --- PAGE 4: GRAPH ---
        elif page == "📈 Spending Graph":
            st.title("📈 Spending Analysis")
            st.bar_chart(df.groupby('Category')['Amount'].sum())
    else:
        if page != "📝 Input Data":
            st.info("Please enter and analyze data in the 'Input Data' page first!")