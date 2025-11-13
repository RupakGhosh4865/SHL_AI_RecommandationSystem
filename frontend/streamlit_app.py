"""
Streamlit Frontend - SHL Assessment Recommender
Beautiful web interface for the recommendation system
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .assessment-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = os.getenv('API_URL', 'https://shl-assessment-api-production-8cd2.up.railway.app/')

# Sidebar
with st.sidebar:
    st.image("https://www.shl.com/wp-content/uploads/2021/06/SHL-Logo.png", width=200)
    st.markdown("## ⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value=API_URL,
        help="FastAPI backend URL"
    )
    
    st.markdown("---")
    st.markdown("## 📊 Statistics")
    
    # Try to get stats from API
    try:
        response = requests.get(f"{api_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            st.metric("Total Assessments", stats.get('total_assessments', 0))
            st.metric("Categories", len(stats.get('categories', {})))
    except:
        st.warning("API not available")
    
    st.markdown("---")
    st.markdown("## ℹ️ About")
    st.info("AI-powered assessment recommendation system using Google Gemini")
    
    st.markdown("---")
    st.markdown("## 🔗 Quick Links")
    st.markdown("- [API Docs](http://localhost:8000/docs)")
    st.markdown("- [SHL Website](https://www.shl.com)")

# Main content
st.markdown('<p class="main-header">🎯 SHL Assessment Recommender</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered assessment recommendations for your hiring needs</p>', unsafe_allow_html=True)

# Instructions
with st.expander("📖 How to Use", expanded=False):
    st.markdown("""
    1. **Enter a job description** in the text area below
    2. Click **"Get Recommendations"** button
    3. Review the **top 10 recommended assessments**
    4. Click on assessment links to learn more
    
    **Example queries:**
    - "Python developer with 5 years experience"
    - "Customer service representative with communication skills"
    - "Data analyst proficient in SQL and Excel"
    """)

# Main input area
st.markdown("### 📝 Enter Job Description")

# Text area for job description
job_description = st.text_area(
    "Paste the complete job description or describe the role:",
    height=200,
    placeholder="""Example:
I am hiring for Java developers who can also collaborate effectively with my business teams. 
Looking for an assessment(s) that can be completed in 45 minutes or less.""",
    help="Provide as much detail as possible for better recommendations"
)

# Action buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    submit_button = st.button("🔍 Get Recommendations", type="primary", use_container_width=True)

with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

with col3:
    example_button = st.button("💡 Load Example", use_container_width=True)

# Handle clear button
if clear_button:
    st.rerun()

# Handle example button
if example_button:
    st.session_state['example_loaded'] = True
    st.rerun()

# Load example if button was clicked
if st.session_state.get('example_loaded'):
    job_description = """I am hiring for Java developers who can also collaborate effectively with my business teams. 
Looking for an assessment(s) that can be completed in 45 minutes or less."""
    st.session_state['example_loaded'] = False

# Process recommendations
if submit_button and job_description:
    with st.spinner("🤖 Analyzing job description and finding best assessments..."):
        try:
            # Call API
            response = requests.post(
                f"{api_url}/recommend",
                json={"query": job_description},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get('recommended_assessments', [])
                
                if recommendations:
                    st.success(f"✅ Found {len(recommendations)} relevant assessments!")
                    
                    # Display recommendations
                    st.markdown("---")
                    st.markdown("## 🎯 Recommended Assessments")
                    
                    for idx, assessment in enumerate(recommendations, 1):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"### {idx}. {assessment['name']}")
                                st.markdown(f"**Description:** {assessment['description']}")
                                st.markdown(f"**Category:** {', '.join(assessment['test_type'])}")
                            
                            with col2:
                                st.metric("Duration", f"{assessment['duration']} min")
                                st.markdown(f"**Remote:** {assessment['remote_support']}")
                                st.markdown(f"**Adaptive:** {assessment['adaptive_support']}")
                            
                            st.markdown(f"🔗 [View Assessment]({assessment['url']})")
                            st.markdown("---")
                    
                    # Export options
                    st.markdown("### 💾 Export Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # JSON export
                        json_str = json.dumps(recommendations, indent=2)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_str,
                            file_name=f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # CSV export
                        import pandas as pd
                        df = pd.DataFrame(recommendations)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                else:
                    st.warning("⚠️ No matching assessments found. Try rephrasing your query.")
            
            else:
                st.error(f"❌ API Error: {response.status_code} - {response.text}")
        
        except requests.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the backend is running at: " + api_url)
            st.code(f"uvicorn api.main:app --host 0.0.0.0 --port 8000", language="bash")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif submit_button:
    st.warning("⚠️ Please enter a job description first!")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Powered by:**")
    st.markdown("- Google Gemini AI")
    st.markdown("- FastAPI")
    st.markdown("- Streamlit")

with col2:
    st.markdown("**Features:**")
    st.markdown("- AI-powered recommendations")
    st.markdown("- Natural language queries")
    st.markdown("- Instant results")

with col3:
    st.markdown("**Links:**")
    st.markdown("- [GitHub](https://github.com)")
    st.markdown("- [Documentation](#)")
    st.markdown("- [Support](#)")