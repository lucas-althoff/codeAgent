"""Streamlit UI for Code Analysis Agent."""

import streamlit as st
from datetime import datetime
from pathlib import Path

from src.ui.api_client import CodeAnalysisClient

favicon_path = Path(__file__).parent.parent / "static" / "images" / "favicon.ico"

st.set_page_config(
    page_title="Mirante - Code Agent",
    page_icon=str(favicon_path) if favicon_path.exists() else "🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #3ea216;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stCodeBlock {
        background-color: #f5f5f5;
    }
    .analysis-result {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3ea216;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3ea216;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def check_api_health(client: CodeAnalysisClient) -> bool:
    """Check if API is available."""
    try:
        health = client.health_check()
        return health.get("status") == "healthy"
    except Exception:
        return False


def initialize_session_state():
    """Initialize session state variables."""
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "current_code" not in st.session_state:
        st.session_state.current_code = ""


def main():
    """Main application function."""
    initialize_session_state()

    logo_path = Path(__file__).parent.parent / "static" / "images" / "mirante.jpg"

    col_logo, col_title = st.columns([1, 4])

    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=120)
        else:
            st.markdown("🤖", unsafe_allow_html=True)

    with col_title:
        st.markdown('<div class="main-header">Mirante - Code Agent</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">AI-Powered Python Code Analysis & Optimization</div>',
            unsafe_allow_html=True,
        )

    # Initialize API client
    api_url = st.sidebar.text_input("API URL", value="http://localhost:8000")
    client = CodeAnalysisClient(base_url=api_url)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # API Health Check
        st.subheader("API Status")
        if st.button("Check API Health", use_container_width=True):
            with st.spinner("Checking API..."):
                if check_api_health(client):
                    st.success("✅ API is healthy")
                else:
                    st.error("❌ API is not available")

        st.divider()

        # Example codes
        st.subheader("📝 Example Code")

        examples = {
            "None": "",
            "Inefficient Loop": """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total

result = calculate_sum([1, 2, 3, 4, 5])""",
            "Missing Type Hints": """def process_data(data, multiplier):
    results = []
    for item in data:
        results.append(item * multiplier)
    return results""",
            "Long Function": """def process_order(order_id, customer_name, items, discount, shipping_address, payment_method):
    # Validate order
    if not order_id:
        return None
    if not customer_name:
        return None

    # Calculate total
    total = 0
    for item in items:
        total += item['price'] * item['quantity']

    # Apply discount
    if discount > 0:
        total = total - (total * discount / 100)

    # Add shipping
    if shipping_address['country'] != 'US':
        total += 20

    return total""",
            "Nested Loops": """def find_duplicates(list1, list2):
    duplicates = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                duplicates.append(item1)
    return duplicates""",
        }

        example_choice = st.selectbox(
            "Load an example:",
            list(examples.keys()),
            key="example_selector",
        )

        # Update current_code when example selection changes
        if example_choice in examples:
            if st.session_state.current_code != examples[example_choice]:
                st.session_state.current_code = examples[example_choice]
                st.rerun()

        st.divider()

        # Analysis History
        st.subheader("📊 Recent Analyses")
        if st.button("Load History", use_container_width=True):
            with st.spinner("Loading history..."):
                try:
                    history = client.get_history(limit=5)
                    st.session_state.analysis_history = history.get("items", [])
                    st.success(f"Loaded {history.get('total', 0)} items")
                except Exception as e:
                    st.error(f"Failed to load history: {str(e)}")

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 Code Input")

        # Use session state for the text area
        code_input = st.text_area(
            "Enter your Python code here:",
            value=st.session_state.current_code,
            height=400,
            placeholder="def example():\n    print('Hello, World!')",
        )

        # Update session state if user types in the text area
        if code_input != st.session_state.current_code:
            st.session_state.current_code = code_input

        col_btn1, col_btn2 = st.columns([1, 1])

        with col_btn1:
            analyze_button = st.button(
                "🔍 Analyze Code",
                type="primary",
                use_container_width=True,
            )

        with col_btn2:
            clear_button = st.button(
                "🗑️ Clear",
                use_container_width=True,
            )

        if clear_button:
            st.session_state.current_code = ""
            st.rerun()

    with col2:
        st.header("📊 Analysis Results")

        if analyze_button:
            if not code_input.strip():
                st.warning("⚠️ Please enter some code to analyze.")
            else:
                with st.spinner("🤖 Analyzing your code... This may take a minute."):
                    try:
                        result = client.analyze_code(code_input)

                        # Display success message
                        st.markdown(
                            f'<div class="success-box">✅ Analysis completed successfully!</div>',
                            unsafe_allow_html=True,
                        )

                        # Display analysis ID and timestamp
                        st.caption(f"Analysis ID: {result['analysis_id']}")
                        st.caption(f"Analyzed at: {result['created_at']}")

                        # Display suggestions
                        st.markdown("### 📋 Suggestions")
                        st.markdown(result["suggestions"])

                    except Exception as e:
                        st.markdown(
                            f'<div class="error-box">❌ Analysis failed: {str(e)}</div>',
                            unsafe_allow_html=True,
                        )
        else:
            st.info("👈 Enter your Python code and click 'Analyze Code' to get started!")

            # Show example of what the analysis looks like
            with st.expander("ℹ️ What kind of analysis will I get?"):
                st.markdown("""
                Our AI agents will analyze your code from multiple angles:

                **🚀 Performance Analysis**
                - Algorithmic complexity (Big O notation)
                - Data structure optimization
                - Python-specific performance improvements
                - Resource management

                **🎯 Code Quality Analysis**
                - SOLID principles compliance
                - Code smells detection
                - Clean code practices
                - PEP 8 style compliance

                **📝 Consolidated Report**
                - Prioritized recommendations
                - Specific, actionable guidance
                - Code examples
                - Impact assessment
                """)

    # Display history in expandable section
    if st.session_state.analysis_history:
        st.divider()
        st.header("📜 Analysis History")

        for idx, item in enumerate(st.session_state.analysis_history):
            with st.expander(
                f"Analysis {idx + 1} - {item.get('created_at', 'Unknown time')}"
            ):
                st.code(item.get("code_snippet", ""), language="python")
                if item.get("suggestions"):
                    st.markdown("**Suggestions:**")
                    st.markdown(item["suggestions"])

    # Footer
    st.divider()
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.caption("Powered by CrewAI")
    with col_f2:
        st.caption("Built with FastAPI & Streamlit")
    with col_f3:
        st.caption("Version 1.0.0")


if __name__ == "__main__":
    main()
