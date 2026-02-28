import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import json

# Page config
st.set_page_config(
    page_title="T20 Score Predictor",
    page_icon="cricket",
    layout="wide"
)


HISTORY_FILE = "history.json"

# Helper function to load prediction history from file
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# Helper function to save prediction history to file
def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception:
        pass

# Initialize session state for history
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = load_history()

# Initialize session state for showing prediction
if 'show_prediction' not in st.session_state:
    st.session_state.show_prediction = False

# Initialize session state for last prediction
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None

# Initialize widget default values (first load only)
if 'batting_team' not in st.session_state:
    st.session_state.batting_team = 'India'
if 'bowling_team' not in st.session_state:
    st.session_state.bowling_team = 'Australia'
if 'city' not in st.session_state:
    st.session_state.city = 'Mumbai'
if 'current_score' not in st.session_state:
    st.session_state.current_score = 50
if 'overs' not in st.session_state:
    st.session_state.overs = 8.0
if 'wickets' not in st.session_state:
    st.session_state.wickets = 2
if 'last_five' not in st.session_state:
    st.session_state.last_five = 35

# Handle clear form action (must happen before widgets render)
if 'clear_form_action' in st.session_state and st.session_state.clear_form_action:
    st.session_state.clear_form_action = False
    # Clear all fields to empty/placeholder state
    st.session_state.batting_team = '-- Select Team --'
    st.session_state.bowling_team = '-- Select Team --'
    st.session_state.city = '-- Select City --'
    st.session_state.current_score = 0
    st.session_state.overs = 5.0  # Minimum allowed by model
    st.session_state.wickets = 0
    st.session_state.last_five = 0
    st.session_state.show_prediction = False
    st.session_state.last_prediction = None
    st.rerun()

# Handle load history action (must happen before widgets render)
if 'load_history_action' in st.session_state and st.session_state.load_history_action is not None:
    idx = st.session_state.load_history_action
    st.session_state.load_history_action = None
    if idx < len(st.session_state.prediction_history):
        item = st.session_state.prediction_history[idx]
        # Set widget values directly
        st.session_state.batting_team = item['batting_team']
        st.session_state.bowling_team = item['bowling_team']
        st.session_state.city = item['city']
        st.session_state.current_score = item['current_score']
        st.session_state.overs = item['overs']
        st.session_state.wickets = item['wickets']
        st.session_state.last_five = item['last_five']
        st.session_state.show_prediction = True
        st.session_state.last_prediction = item['predicted_score']
        st.rerun()

# Function to save to history and persist to file
def save_to_history(batting_team, bowling_team, city, current_score, overs, wickets, last_five, predicted_score):
    # Add to history (limit to 10 items)
    history_item = {
        'batting_team': batting_team,
        'bowling_team': bowling_team,
        'city': city,
        'current_score': current_score,
        'overs': overs,
        'wickets': wickets,
        'last_five': last_five,
        'predicted_score': predicted_score,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.prediction_history.insert(0, history_item)
    if len(st.session_state.prediction_history) > 10:
        st.session_state.prediction_history.pop()
    save_history(st.session_state.prediction_history)

# Custom CSS with cricket-themed background
st.markdown("""
<style>
    /* Cricket field background */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        background-image: 
            radial-gradient(ellipse at center, rgba(34, 139, 34, 0.1) 0%, transparent 50%),
            linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    }
    
    /* Cricket pitch pattern overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 50px,
                rgba(34, 139, 34, 0.03) 50px,
                rgba(34, 139, 34, 0.03) 51px
            ),
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 50px,
                rgba(34, 139, 34, 0.03) 50px,
                rgba(34, 139, 34, 0.03) 51px
            );
        pointer-events: none;
        z-index: 0;
    }
    
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #228B22 0%, #006400 100%);
        color: white;
        font-size: 18px;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        margin-top: 1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #32CD32 0%, #228B22 100%);
    }
    .prediction-box {
        background: linear-gradient(135deg, #228B22 0%, #006400 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 1rem;
        border: 2px solid #32CD32;
    }
    .prediction-text {
        color: white;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .prediction-score {
        color: #FFD700;
        font-size: 3.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .match-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: 2px solid #228B22;
    }
    .team-badge {
        background: linear-gradient(135deg, #228B22 0%, #006400 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.25rem;
        color: white;
    }
    .stat-card {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #228B22;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #32CD32;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #a2a8d3;
    }
    .live-prediction {
        background: linear-gradient(135deg, #228B22 0%, #006400 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        border: 2px solid #FFD700;
    }
    .live-score {
        font-size: 3rem;
        font-weight: bold;
        color: #FFD700;
    }
    .vs-text {
        font-size: 1.2rem;
        color: #FFD700;
        font-weight: bold;
    }
    .section-header {
        color: #32CD32;
        border-bottom: 2px solid #228B22;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    /* Style for selectbox and inputs */
    .stSelectbox label, .stNumberInput label {
        color: #a2a8d3 !important;
    }
    /* History item styling */
    .history-item {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #228B22;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .history-item:hover {
        border-color: #FFD700;
        transform: translateX(5px);
    }
    .history-teams {
        font-size: 0.9rem;
        color: #32CD32;
        font-weight: bold;
    }
    .history-details {
        font-size: 0.75rem;
        color: #a2a8d3;
        margin-top: 0.25rem;
    }
    .history-score {
        font-size: 1.1rem;
        color: #FFD700;
        font-weight: bold;
    }
    .clear-btn {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    return pickle.load(open('./Model/pipe.pkl', 'rb'))

pipe = load_model()

teams = ['Australia', 'India', 'Bangladesh', 'New Zealand', 'South Africa',
         'England', 'West Indies', 'Afghanistan', 'Pakistan', 'Sri Lanka']

cities = ['Colombo', 'Mirpur', 'Johannesburg', 'Dubai', 'Auckland', 'Cape Town',
          'London', 'Pallekele', 'Barbados', 'Sydney', 'Melbourne', 'Durban',
          'St Lucia', 'Wellington', 'Lauderhill', 'Hamilton', 'Centurion',
          'Manchester', 'Abu Dhabi', 'Mumbai', 'Nottingham', 'Southampton',
          'Mount Maunganui', 'Chittagong', 'Kolkata', 'Lahore', 'Delhi',
          'Nagpur', 'Chandigarh', 'Adelaide', 'Bangalore', 'St Kitts',
          'Cardiff', 'Christchurch', 'Trinidad']

# Create three columns - Main content, Dashboard, and History
main_col, dashboard_col, history_col = st.columns([2, 1, 1])

with main_col:
    # Header
    st.markdown("# T20 Score Predictor")
    st.markdown("*Predict the final score based on current match situation*")
    
    st.divider()

    # Team Selection
    st.markdown('<h3 class="section-header">Teams</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Add placeholder option for empty state
    team_options = ['-- Select Team --'] + sorted(teams)
    city_options = ['-- Select City --'] + sorted(cities)

    with col1:
        batting_team = st.selectbox('Batting Team', team_options, key='batting_team')
    with col2:
        bowling_team = st.selectbox('Bowling Team', team_options, key='bowling_team')

    # Validation: teams should be selected and different
    teams_selected = batting_team != '-- Select Team --' and bowling_team != '-- Select Team --'
    if teams_selected and batting_team == bowling_team:
        st.warning("Please select different teams for batting and bowling")
    elif not teams_selected:
        st.info("Please select both batting and bowling teams")

    # Venue
    st.markdown('<h3 class="section-header">Venue</h3>', unsafe_allow_html=True)
    city = st.selectbox('Select Match City', city_options, key='city')

    st.divider()

    # Match Situation
    st.markdown('<h3 class="section-header">Current Match Situation</h3>', unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)

    with col3:
        current_score = st.number_input('Current Score', min_value=0, max_value=400, 
                                        step=1, key='current_score')
    with col4:
        overs = st.number_input('Overs Completed', min_value=5.0, max_value=20.0, 
                               step=0.1, help="Model works best for overs > 5", key='overs')
    with col5:
        wickets = st.number_input('Wickets Lost', min_value=0, max_value=10, 
                                  step=1, key='wickets')

    last_five = st.number_input('Runs in Last 5 Overs', min_value=0, max_value=120, 
                                step=1, help="Total runs scored in the last 5 overs", key='last_five')
    
    st.divider()
    
    # Buttons row
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        predict_clicked = st.button("Predict Score", key="predict_btn", type="primary", use_container_width=True)
    with btn_col2:
        if st.button("Clear Form", key="clear_btn", type="secondary", use_container_width=True):
            st.session_state.clear_form_action = True
            st.rerun()

# Calculate live stats
balls_left = int(120 - (overs * 6))
wickets_left = int(10 - wickets)
crr = current_score / overs if overs > 0 else 0
balls_faced = int(overs * 6)
overs_left = (120 - balls_faced) / 6

# Live prediction (always calculate)
teams_valid = batting_team != '-- Select Team --' and bowling_team != '-- Select Team --' and batting_team != bowling_team
city_valid = city != '-- Select City --'
valid_input = teams_valid and city_valid and overs >= 5 and wickets <= 10
if valid_input:
    input_df = pd.DataFrame({
        'batting_team': [batting_team],
        'bowling_team': [bowling_team],
        'city': [city],
        'current_score': [current_score],
        'balls_left': [balls_left],
        'wickets_left': [wickets_left],
        'crr': [crr],
        'last_five': [last_five]
    })
    predicted_score = int(pipe.predict(input_df)[0])
    runs_to_add = predicted_score - current_score
    required_rate = runs_to_add / overs_left if overs_left > 0 else 0
    
    # Only save to history when Predict button is clicked
    if predict_clicked:
        save_to_history(batting_team, bowling_team, city, current_score, overs, wickets, last_five, predicted_score)
        st.session_state.show_prediction = True
        st.session_state.last_prediction = predicted_score
else:
    predicted_score = None
    runs_to_add = None
    required_rate = None

# History Column
with history_col:
    st.markdown("## Prediction History")
    
    if st.button("Clear All History", key="clear_history_btn", type="secondary"):
        st.session_state.prediction_history = []
        save_history(st.session_state.prediction_history)
        st.rerun()
    
    st.divider()
    
    if len(st.session_state.prediction_history) == 0:
        st.info("No predictions yet. Click 'Predict Score' to add predictions here.")
    else:
        for idx, item in enumerate(st.session_state.prediction_history):
            # Create a clickable container for each history item
            with st.container():
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-teams">{item['batting_team']} vs {item['bowling_team']}</div>
                    <div class="history-details">{item['city']} | {item['current_score']}/{item['wickets']} ({item['overs']} ov)</div>
                    <div class="history-score">Predicted: {item['predicted_score']}</div>
                    <div style="font-size: 0.7rem; color: #666;">{item['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Load", key=f"load_{idx}", use_container_width=True):
                    st.session_state.load_history_action = idx
                    st.rerun()

# Dashboard Column (Sidebar)
with dashboard_col:
    st.markdown("## Live Dashboard")
    
    # Match Info Card
    st.markdown(f"""
    <div class="match-card">
        <div style="text-align: center;">
            <span class="team-badge">{batting_team}</span>
            <span class="vs-text"> VS </span>
            <span class="team-badge">{bowling_team}</span>
        </div>
        <div style="text-align: center; margin-top: 1rem; color: #a2a8d3;">
            {city}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Current Score Display
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{current_score}/{wickets}</div>
        <div class="stat-label">Current Score</div>
        <div style="color: #a2a8d3; margin-top: 0.5rem;">({overs} overs)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Grid
    stat1, stat2 = st.columns(2)
    with stat1:
        st.metric("Balls Left", balls_left)
        st.metric("Run Rate", f"{crr:.2f}")
    with stat2:
        st.metric("Wickets Left", wickets_left)
        st.metric("Last 5 Ovs", last_five)
    
    # Progress Bars
    st.markdown("#### Match Progress")
    
    # Overs progress
    overs_progress = (overs / 20) * 100
    st.progress(overs_progress / 100, text=f"Overs: {overs}/20")
    
    # Wickets progress
    wickets_progress = (wickets / 10) * 100
    st.progress(wickets_progress / 100, text=f"Wickets: {wickets}/10")
    
    st.divider()
    
    # Live Prediction - only show after clicking Predict
    st.markdown("### Prediction Result")
    
    if st.session_state.show_prediction and valid_input and predicted_score is not None:
        st.markdown(f"""
        <div class="live-prediction">
            <div style="color: white; font-size: 0.9rem;">Predicted Final Score</div>
            <div class="live-score">{predicted_score}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prediction insights
        st.markdown(f"""
        <div class="stat-card">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div class="stat-label">Runs to Add</div>
                    <div style="font-size: 1.5rem; color: #32CD32;">{runs_to_add}</div>
                </div>
                <div>
                    <div class="stat-label">Req. Rate</div>
                    <div style="font-size: 1.5rem; color: #FFD700;">{required_rate:.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif not valid_input:
        st.warning("Fix input errors to see prediction")
    else:
        st.info("Click 'Predict Score' to see prediction")

# Charts Section in Main Column
with main_col:
    st.divider()
    st.markdown('<h3 class="section-header">Analytics Dashboard</h3>', unsafe_allow_html=True)
    
    if st.session_state.show_prediction and valid_input:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Run Rate Comparison Chart
            fig_rr = go.Figure()
            
            fig_rr.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=crr,
                delta={'reference': required_rate, 'relative': False},
                title={'text': "Current Run Rate", 'font': {'size': 16, 'color': 'white'}},
                gauge={
                    'axis': {'range': [0, 15], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#32CD32"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "#228B22",
                    'steps': [
                        {'range': [0, 6], 'color': 'rgba(255,0,0,0.3)'},
                        {'range': [6, 10], 'color': 'rgba(255,255,0,0.3)'},
                        {'range': [10, 15], 'color': 'rgba(0,255,0,0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "#FFD700", 'width': 4},
                        'thickness': 0.75,
                        'value': required_rate
                    }
                }
            ))
            
            fig_rr.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "white"},
                height=250,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_rr, use_container_width=True)
        
        with chart_col2:
            # Score Projection Bar Chart
            scenarios = ['Conservative', 'Predicted', 'Aggressive']
            scores = [int(predicted_score * 0.9), predicted_score, int(predicted_score * 1.1)]
            colors = ['#FF6B6B', '#32CD32', '#4ECDC4']
            
            fig_proj = go.Figure(data=[
                go.Bar(
                    x=scenarios,
                    y=scores,
                    marker_color=colors,
                    text=scores,
                    textposition='outside',
                    textfont={'color': 'white', 'size': 14}
                )
            ])
            
            fig_proj.update_layout(
                title={'text': 'Score Projections', 'font': {'color': 'white', 'size': 16}},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                yaxis={'gridcolor': 'rgba(255,255,255,0.1)', 'showgrid': True},
                xaxis={'showgrid': False}
            )
            st.plotly_chart(fig_proj, use_container_width=True)
        
        # Second row of charts
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Innings Progress Pie Chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Runs Scored', 'Runs to Add'],
                values=[current_score, runs_to_add],
                hole=0.6,
                marker_colors=['#32CD32', '#0f3460'],
                textinfo='label+value',
                textfont={'color': 'white'}
            )])
            
            fig_pie.update_layout(
                title={'text': 'Score Breakdown', 'font': {'color': 'white', 'size': 16}},
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False,
                annotations=[{
                    'text': f'{predicted_score}',
                    'x': 0.5, 'y': 0.5,
                    'font_size': 24,
                    'font_color': '#FFD700',
                    'showarrow': False
                }]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with chart_col4:
            # Projected Over-by-Over Run Rate
            remaining_overs = int(20 - overs)
            over_numbers = list(range(int(overs) + 1, 21))
            
            # Simulate projected run rates
            projected_rr = [required_rate * (1 + (i - int(overs)) * 0.05) for i in range(int(overs) + 1, 21)]
            
            fig_line = go.Figure()
            
            # Current run rate line
            fig_line.add_hline(y=crr, line_dash="dash", line_color="#32CD32", 
                              annotation_text=f"Current RR: {crr:.2f}")
            
            # Required run rate line
            fig_line.add_hline(y=required_rate, line_dash="dot", line_color="#FFD700",
                              annotation_text=f"Required RR: {required_rate:.2f}")
            
            fig_line.add_trace(go.Scatter(
                x=over_numbers,
                y=projected_rr,
                mode='lines+markers',
                name='Projected RR',
                line={'color': '#4ECDC4', 'width': 2},
                marker={'size': 6}
            ))
            
            fig_line.update_layout(
                title={'text': 'Projected Run Rate Trend', 'font': {'color': 'white', 'size': 16}},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis={'title': 'Overs', 'gridcolor': 'rgba(255,255,255,0.1)'},
                yaxis={'title': 'Run Rate', 'gridcolor': 'rgba(255,255,255,0.1)'},
                showlegend=False
            )
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Enter valid match data to see analytics")

# Footer
with main_col:
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #808495; padding: 1rem;">
        <p>Built using Machine Learning | Data from International T20 Matches</p>
    </div>
    """, unsafe_allow_html=True)


