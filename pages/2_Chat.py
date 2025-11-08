"""
Chat Interface - Main chatbot page with report generation
"""
import streamlit as st
import sys
import os
from agents.task_planner import TaskPlannerAgent
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.web_research_agent import WebResearchAgent
from agents.memory import MemoryManager
from agents.structured_data_agent import StructuredDataAgent
from agents.rag_agent import RAGAgent
from agents.renovation_agent import RenovationAgent
from agents.query_router import QueryRouter
from agents.report_agent import ReportAgent
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

# Initialize session state
if 'memory' not in st.session_state:
    st.session_state.memory = MemoryManager()
if 'task_planner' not in st.session_state:
    st.session_state.task_planner = TaskPlannerAgent()
if 'structured_agent' not in st.session_state:
    st.session_state.structured_agent = StructuredDataAgent()

if 'rag_agent' not in st.session_state:
    st.session_state.rag_agent = RAGAgent()

if 'research_agent' not in st.session_state:
    st.session_state.research_agent = WebResearchAgent()

if 'renovation_agent' not in st.session_state:
    st.session_state.renovation_agent = RenovationAgent()

if 'router' not in st.session_state:
    st.session_state.router = QueryRouter()

if 'report_agent' not in st.session_state:
    st.session_state.report_agent = ReportAgent()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'last_search_results' not in st.session_state:
    st.session_state.last_search_results = []

# Helper functions
# def handle_search(params, query):
#     """Handle property search"""
#     results = st.session_state.structured_agent.search_properties(params)
    
#     # Store results for potential report generation
#     st.session_state.last_search_results = results
    
#     if results:
#         st.write(f"**Found {len(results)} properties:**")
#         for i, prop in enumerate(results[:10], 1):
#             with st.expander(f" {prop.get('location', 'Property')} - ${prop.get('price', 0):,.0f}"):
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.write(f"**ID:** {prop.get('property_id', 'N/A')}")
#                     st.write(f"**Location:** {prop.get('location', 'N/A')}")
#                     st.write(f"**Price:** ${prop.get('price', 0):,.0f}")
#                 with col2:
#                     st.write(f"**Status:** {prop.get('status', 'N/A')}")
#                     st.write(f"**Description:** {prop.get('long_description', 'N/A')[:100]}...")
        
#         st.session_state.memory.add_search(query, len(results))
        
#         # Offer to generate report
#         if st.button(" Generate Report from These Results"):
#             return handle_report_generation(results)
        
#         return f"Found {len(results)} properties"
#     else:
#         return "No properties found. Try different search criteria."
def handle_complex_query(query):
    """Handle multi-step queries using task planner"""
    planner = st.session_state.task_planner
    
    # Check if complex
    if planner.is_complex_query(query):
        st.info("Detected multi-step query. Breaking it down...")
        
        # Decompose into tasks
        tasks = planner.decompose_query(query)
        
        # Show execution plan
        with st.expander("Execution Plan", expanded=True):
            for task in tasks:
                st.write(f"**Step {task['step']}:** {task['description']}")
        
        st.markdown("---")
        
        # Execute each task
        results = []
        for task in tasks:
            st.write(f"**Executing Step {task['step']}...**")
            
            if task['action'] == 'search_properties':
                route = st.session_state.router.route_query(query)
                result = handle_search(route['params'], query)
                results.append(result)
            
            elif task['action'] == 'estimate_renovation':
                route = st.session_state.router.route_query(query)
                result = handle_renovation(route['params'])
                results.append(result)
            
            elif task['action'] == 'generate_report':
                result = handle_report_generation()
                results.append(result)
        
        return f"Completed {len(tasks)} steps"
    
    return None


def handle_search(params, query):
    """Handle property search"""
    results = st.session_state.structured_agent.search_properties(params)
    
    # Store results
    st.session_state.last_search_results = results
    
    if results:
        st.success(f"Found {len(results)} properties")
        
        # Display all properties (up to 50)
        for i, prop in enumerate(results, 1):
            with st.expander(f"#{i} - {prop.get('location', 'Property')} - ₹{prop.get('price', 0):,.0f}"):
                st.write(f"**Property ID:** {prop.get('property_id', 'N/A')}")
                st.write(f"**Location:** {prop.get('location', 'N/A')}")
                st.write(f"**Price:** ₹{prop.get('price', 0):,.0f}")
                st.write(f"**Status:** {prop.get('status', 'N/A')}")
                
                # Show description WITHOUT nested expander
                if prop.get('long_description'):
                    st.markdown("**Description:**")
                    desc = prop.get('long_description', '')
                    # Show first 300 characters, then rest in smaller text
                    if len(desc) > 300:
                        st.write(desc[:300] + "...")
                        st.caption(desc[300:])
                    else:
                        st.write(desc)
        
        # Generate report button
        # st.markdown("---")
        # if st.button("Generate PDF Report", key="gen_report"):
        #     return handle_report_generation(results)
        
        st.session_state.memory.add_search(query, len(results))
        return f"Displayed {len(results)} properties"
    else:
        st.warning("No properties found.")
        return "No properties found."
def handle_report_generation(properties=None):
    """Generate and download PDF report"""
    if properties is None:
        properties = st.session_state.last_search_results
    
    if not properties:
        st.warning("No properties to generate report from. Please search first.")
        return "No data available for report"
    
    try:
        # Get statistics
        stats = st.session_state.structured_agent.get_statistics()
        
        # Generate report
        with st.spinner("Generating PDF report..."):
            filename = f"property_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = st.session_state.report_agent.generate_summary_report(
                properties, stats, filename
            )
        
        # Provide download button
        with open(filepath, 'rb') as f:
            st.download_button(
                label="Download Report",
                data=f,
                file_name=filename,
                mime='application/pdf'
            )
        
        st.success(f"Report generated successfully! ({len(properties)} properties)")
        return f"Report generated with {len(properties)} properties"
        
    except Exception as e:
        st.error(f"Error generating report: {e}")
        return f"Error: {e}"

def display_statistics():
    """Display statistics"""
    stats = st.session_state.structured_agent.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", stats.get('total_properties', 0))
    with col2:
        st.metric("Avg Price", f"${stats.get('avg_price', 0):,.0f}")
    with col3:
        st.metric("Min Price", f"${stats.get('min_price', 0):,.0f}")
    with col4:
        st.metric("Max Price", f"${stats.get('max_price', 0):,.0f}")
    
    # # Offer to generate statistical report
    # if st.button("Generate Statistics Report"):
    #     properties = st.session_state.structured_agent.search_properties({})
    #     return handle_report_generation(properties)
    
    return "Statistics displayed"

def handle_renovation(params):
    """Handle renovation estimation"""
    sqft = params.get('square_feet', 1500)
    reno_type = params.get('renovation_type', 'moderate')
    
    estimate = st.session_state.renovation_agent.estimate_cost(sqft, reno_type)
    
    st.write(f"**Estimated Cost:** ${estimate['total_estimate']:,.2f}")
    st.write(f"**Property Size:** {sqft} sq ft")
    st.write(f"**Type:** {reno_type.title()}")
    
    with st.expander("See breakdown"):
        for item, cost in estimate['breakdown'].items():
            st.write(f"- {item.title()}: ${cost:,.2f}")
    
    return f"Renovation estimate: ${estimate['total_estimate']:,.2f}"

def handle_research(params, query):
    """Handle market research queries"""
    # Extract location from query
    location = params.get('city') or params.get('location', 'Mumbai')
    
    st.subheader(f"Market Research: {location}")
    
    # Get market data
    market_data = st.session_state.research_agent.research_market_rates(location)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg Price/Sqft", f"₹{market_data['avg_price_per_sqft']:,}")
        st.metric("Market Trend", market_data['market_trend'])
    with col2:
        st.metric("Growth Rate", f"{market_data['growth_rate']}%")
        st.metric("Demand Level", market_data['demand_level'])
    
    st.write("**Market Insights:**")
    for insight in market_data['insights']:
        st.write(f"- {insight}")
    # return ""
    return f"Market research completed for {location}"

def process_intent(intent, params, query):
    """Process user intent"""
    if intent == 'search_properties':
        return handle_search(params, query)
    elif intent == 'get_statistics':
        return display_statistics()
    elif intent == 'estimate_renovation':
        return handle_renovation(params)
    elif intent == 'generate_report':
        return handle_report_generation()
    elif intent == 'web_research': 
        return handle_research(params, query)
    elif intent == 'view_saved':
        saved = st.session_state.memory.get_saved_properties()
        if saved:
            st.write(f"**You have {len(saved)} saved properties:**")
            for item in saved:
                st.write(f"- {item['info'].get('title', 'Property')}")
        return f"{len(saved)} saved properties"
    else:
        return handle_search(params, query)

# Main UI
st.title("Real Estate Assistant")
st.markdown("Ask me about properties, get estimates, and generate reports!")

# Example queries
with st.expander("💡 Try these examples"):
    examples = [
        "Show statistics",
        "Generate report",
        "Properties in Hyderabad",
        "Properties under 25000000",
        "Find properties in Hyderabad and estimate renovation costs",
        "Estimate renovation for 1500 sq ft",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state.chat_history.append({
                'user': ex,
                'bot': 'processing'
            })
            st.rerun()

st.markdown("---")

# Display chat history
for i, chat in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.write(chat['user'])
    
    with st.chat_message("assistant"):
        if chat['bot'] == 'processing':
            # Process the query
            route = st.session_state.router.route_query(chat['user'])
            response = process_intent(route['intent'], route['params'], chat['user'])
            st.session_state.chat_history[i]['bot'] = response
        else:
            st.write(chat['bot'])

# # Display chat history
# for i, chat in enumerate(st.session_state.chat_history):
#     with st.chat_message("user"):
#         st.write(chat['user'])
    
#     with st.chat_message("assistant"):
#         if chat['bot'] == 'processing':
#             # Process the query
#             route = st.session_state.router.route_query(chat['user'])
#             response = process_intent(route['intent'], route['params'], chat['user'])
#             st.session_state.chat_history[i]['bot'] = response
#             # Don't display text here - process_intent already displayed it
#         elif chat['bot'] in ['statistics_requested', 'saved_properties']:
#             # Re-execute these to show results
#             route = st.session_state.router.route_query(chat['user'])
#             process_intent(route['intent'], route['params'], chat['user'])
#         else:
#             # Only show text for simple responses
#             if not chat['bot'].startswith('Market research'):
#                 st.write(chat['bot'])

# Chat input
user_input = st.chat_input("Ask about properties...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    route = st.session_state.router.route_query(user_input)
    
    with st.chat_message("assistant"):
        response = process_intent(route['intent'], route['params'], user_input)
    
    st.session_state.memory.add_conversation(user_input, str(response))
    st.session_state.chat_history.append({
        'user': user_input,
        'bot': response
    })
    st.rerun()

# Sidebar
with st.sidebar:
    st.subheader("Quick Stats")
    try:
        stats = st.session_state.structured_agent.get_statistics()
        st.metric("Properties", stats.get('total_properties', 0))
        st.metric("Searches", len(st.session_state.memory.memory.get('search_history', [])))
    except:
        pass
    
    st.markdown("---")
    
    st.subheader("Reports")
    if st.button("Generate Full Report"):
        properties = st.session_state.structured_agent.search_properties({})
        handle_report_generation(properties)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
