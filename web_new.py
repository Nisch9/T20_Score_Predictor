import streamlit as st
import os
import json
import pickle
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="T20 Score Predictor",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
HIST_FILE = 'history.json'
if 'prediction_history' not in st.session_state:
    # Try to load from file
    if os.path.exists(HIST_FILE):
        try:
            with open(HIST_FILE, 'r') as f:
                st.session_state.prediction_history = json.load(f)
        except Exception:
            st.session_state.prediction_history = []
    else:
        st.session_state.prediction_history = []
if 'show_prediction' not in st.session_state:
    st.session_state.show_prediction = False
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None

# Widget defaults
defaults = {'batting_team': '-- Select --', 'bowling_team': '-- Select --', 'city': '-- Select --',
            'current_score': 50, 'overs': 8.0, 'wickets': 2, 'last_five': 35}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Clear form action handler
if st.session_state.get('clear_form_action'):
    st.session_state.clear_form_action = False
    for key, val in defaults.items():
        st.session_state[key] = '-- Select --' if 'team' in key or key == 'city' else (0 if key != 'overs' else 5.0)
    st.session_state.show_prediction = False
    st.rerun()

# Load history action handler
if st.session_state.get('load_history_action') is not None:
    idx = st.session_state.load_history_action
    st.session_state.load_history_action = None
    if idx < len(st.session_state.prediction_history):
        item = st.session_state.prediction_history[idx]
        for key in ['batting_team', 'bowling_team', 'city', 'current_score', 'overs', 'wickets', 'last_five']:
            st.session_state[key] = item[key]
        st.session_state.show_prediction = True
        st.session_state.last_prediction = item['predicted_score']
        st.rerun()

# Save to history function
def save_to_history(data, score):
    item = {**data, 'predicted_score': score, 'timestamp': datetime.now().strftime("%H:%M")}
    st.session_state.prediction_history.insert(0, item)
    if len(st.session_state.prediction_history) > 8:
        st.session_state.prediction_history.pop()
    # Save to file
    try:
        with open(HIST_FILE, 'w') as f:
            json.dump(st.session_state.prediction_history, f)
    except Exception:
        pass

# Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding: 1rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .main-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    .main-subtitle {
        font-size: 0.8rem;
        color: #a7f3d0;
        margin: 0;
    }
    
    /* Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .card-header {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* Team Display */
    .match-display {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 0.5rem 0;
    }
    .team-name {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        color: white;
        font-size: 0.9rem;
    }
    .vs-badge {
        color: #fbbf24;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    /* Big Score */
    .big-score {
        text-align: center;
        padding: 0.5rem 0;
    }
    .score-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #10b981;
    }
    .score-info {
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
    /* Prediction Box */
    .prediction-box {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        border: 2px solid #fbbf24;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .prediction-label {
        font-size: 0.7rem;
        color: #a7f3d0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .prediction-value {
        font-size: 2.8rem;
        font-weight: 700;
        color: #fbbf24;
        line-height: 1;
    }
    .prediction-detail {
        font-size: 0.75rem;
        color: white;
        margin-top: 0.3rem;
    }
    
    /* Stats Grid */
    .stat-item {
        text-align: center;
        padding: 0.5rem;
    }
    .stat-num {
        font-size: 1.3rem;
        font-weight: 600;
        color: #10b981;
    }
    .stat-label {
        font-size: 0.65rem;
        color: #94a3b8;
        text-transform: uppercase;
    }
    
    /* History Items */
    .history-item {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        margin-bottom: 0.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .history-teams {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 500;
    }
    .history-score {
        font-size: 0.9rem;
        color: #fbbf24;
        font-weight: 600;
    }
    
    /* Form styling */
    .stSelectbox label, .stNumberInput label {
        font-size: 0.75rem !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    .stSelectbox > div > div, .stNumberInput > div > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4) !important;
    }
    
    /* Progress */
    .progress-container {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 10px;
        height: 8px;
        margin: 0.3rem 0;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Metric overrides */
    [data-testid="stMetric"] {
        background: transparent !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        color: #10b981 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        color: #94a3b8 !important;
    }
    
    /* Hide default elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
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

# Header
st.markdown("""
<div class="main-header">
    <div>
        <p class="main-title">T20 Score Predictor</p>
        <p class="main-subtitle">Machine Learning Powered Analysis</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Layout: 3 columns
col_form, col_result, col_history = st.columns([1.2, 1.3, 0.8])

# --- Helper: Hide prediction on any input change ---
def hide_prediction_on_change():
    st.session_state.show_prediction = False


# FORM COLUMN
with col_form:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="card-header">Match Setup</p>', unsafe_allow_html=True)
    
    team_opts = ['-- Select --'] + sorted(teams)
    city_opts = ['-- Select --'] + sorted(cities)
    
    c1, c2 = st.columns(2)
    with c1:
        batting_team = st.selectbox('Batting', team_opts, key='batting_team', on_change=hide_prediction_on_change)
    with c2:
        bowling_team = st.selectbox('Bowling', team_opts, key='bowling_team', on_change=hide_prediction_on_change)
    city = st.selectbox('Venue', city_opts, key='city', on_change=hide_prediction_on_change)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="card-header">Current Situation</p>', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3:
        current_score = st.number_input('Score', 0, 400, key='current_score', on_change=hide_prediction_on_change)
        wickets = st.number_input('Wickets', 0, 10, key='wickets', on_change=hide_prediction_on_change)
    with c4:
        overs = st.number_input('Overs', 5.0, 20.0, step=0.1, key='overs', on_change=hide_prediction_on_change)
        last_five = st.number_input('Last 5 Overs', 0, 120, key='last_five', on_change=hide_prediction_on_change)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Buttons
    b1, b2 = st.columns(2)
    with b1:
        predict = st.button("Predict Score", use_container_width=True, type="primary")
    with b2:
        if st.button("Clear", use_container_width=True):
            st.session_state.clear_form_action = True
            st.rerun()

# Calculate stats
balls_left = max(0, int(120 - (overs * 6)))
wickets_left = 10 - wickets
crr = current_score / overs if overs > 0 else 0
overs_left = (120 - int(overs * 6)) / 6

# Validation
valid = (batting_team not in ['-- Select --'] and 
         bowling_team not in ['-- Select --'] and 
         batting_team != bowling_team and
         city != '-- Select --' and overs >= 5)

# Prediction
predicted_score = runs_to_add = required_rate = None
if valid:
    input_df = pd.DataFrame({
        'batting_team': [batting_team], 'bowling_team': [bowling_team], 'city': [city],
        'current_score': [current_score], 'balls_left': [balls_left],
        'wickets_left': [wickets_left], 'crr': [crr], 'last_five': [last_five]
    })
    predicted_score = int(pipe.predict(input_df)[0])
    runs_to_add = predicted_score - current_score
    required_rate = runs_to_add / overs_left if overs_left > 0 else 0
    
    if predict:
        save_to_history({
            'batting_team': batting_team, 'bowling_team': bowling_team, 'city': city,
            'current_score': current_score, 'overs': overs, 'wickets': wickets, 'last_five': last_five
        }, predicted_score)
        st.session_state.show_prediction = True
        st.session_state.last_prediction = predicted_score

# RESULT COLUMN
with col_result:
    # Match Display
    if valid:
        st.markdown(f"""
        <div class="glass-card">
            <div class="match-display">
                <span class="team-name">{batting_team}</span>
                <span class="vs-badge">VS</span>
                <span class="team-name">{bowling_team}</span>
            </div>
            <p style="text-align:center;color:#94a3b8;font-size:0.75rem;margin:0;">{city}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current Score Display
        st.markdown(f"""
        <div class="glass-card">
            <div class="big-score">
                <div class="score-value">{current_score}/{wickets}</div>
                <div class="score-info">{overs} overs • Run Rate: {crr:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prediction Display
        if st.session_state.show_prediction and valid and predicted_score is not None:
            st.markdown(f"""
            <div class="prediction-box">
                <p class="prediction-label">Predicted Final Score</p>
                <p class="prediction-value">{predicted_score}</p>
                <p class="prediction-detail">+{runs_to_add} runs needed • RRR: {required_rate:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            # Three charts in a single row, fixed heights
            with st.container():
                chart1, chart2, chart3 = st.columns([1,1,1])
                with chart1:
                    # Run Rate Gauge
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=crr,
                        title={'text': "Current RR", 'font': {'size': 12, 'color': 'white'}},
                        number={'font': {'size': 24, 'color': '#10b981'}},
                        gauge={
                            'axis': {'range': [0, 15], 'tickcolor': 'white', 'tickfont': {'color': 'white', 'size': 8}},
                            'bar': {'color': '#10b981'},
                            'bgcolor': 'rgba(30,41,59,0.5)',
                            'bordercolor': 'rgba(255,255,255,0.1)',
                            'steps': [
                                {'range': [0, 6], 'color': 'rgba(239,68,68,0.3)'},
                                {'range': [6, 10], 'color': 'rgba(251,191,36,0.3)'},
                                {'range': [10, 15], 'color': 'rgba(16,185,129,0.3)'}
                            ],
                            'threshold': {
                                'line': {'color': '#fbbf24', 'width': 3},
                                'thickness': 0.8,
                                'value': required_rate
                            }
                        }
                    ))
                    fig_gauge.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'},
                        height=180,
                        margin=dict(l=10, r=10, t=35, b=5)
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                with chart2:
                    # Runs Breakdown Donut
                    percent_complete = int(current_score/predicted_score*100) if predicted_score else 0
                    fig_donut = go.Figure(data=[go.Pie(
                        labels=['Scored', 'To Add'],
                        values=[current_score, max(0, runs_to_add)],
                        hole=0.65,
                        marker_colors=['#10b981', '#1e293b'],
                        textinfo='none',
                        hovertemplate='%{label}: %{value}<extra></extra>'
                    )])
                    fig_donut.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'},
                        height=180,
                        margin=dict(l=10, r=10, t=10, b=10),
                        showlegend=False,
                        annotations=[{
                            'text': f'<b>{percent_complete}%</b><br><span style="font-size:10px">Complete</span>',
                            'x': 0.5, 'y': 0.5,
                            'font_size': 16,
                            'font_color': '#10b981',
                            'showarrow': False
                        }]
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)
                with chart3:
                    # Score Projections Bar Chart
                    conservative = int(predicted_score * 0.92)
                    aggressive = int(predicted_score * 1.08)
                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=['Conservative', 'Predicted', 'Aggressive'],
                            y=[conservative, predicted_score, aggressive],
                            marker_color=['#ef4444', '#10b981', '#3b82f6'],
                            text=[conservative, predicted_score, aggressive],
                            textposition='outside',
                            textfont={'color': 'white', 'size': 11}
                        )
                    ])
                    fig_bar.update_layout(
                        title={'text': 'Score Projections', 'font': {'color': 'white', 'size': 12}, 'x': 0.5},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'},
                        height=180,
                        margin=dict(l=10, r=10, t=35, b=25),
                        yaxis={'visible': False},
                        xaxis={'tickfont': {'size': 9, 'color': '#94a3b8'}}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:2rem;">
                <p style="color:#94a3b8;margin:0;">Click <strong>Predict Score</strong> to see results</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem;">
            <p style="color:#94a3b8;font-size:1.1rem;margin:0;">Select teams, venue and enter match details</p>
            <p style="color:#64748b;font-size:0.8rem;margin-top:0.5rem;">Minimum 5 overs required</p>
        </div>
        """, unsafe_allow_html=True)

# HISTORY COLUMN
with col_history:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="card-header">Recent Predictions</p>', unsafe_allow_html=True)
    
    if st.button("Clear History", key="clear_hist", use_container_width=True):
        st.session_state.prediction_history = []
        try:
            with open(HIST_FILE, 'w') as f:
                json.dump([], f)
        except Exception:
            pass
        st.rerun()
    
    if not st.session_state.prediction_history:
        st.markdown('<p style="color:#64748b;font-size:0.8rem;text-align:center;padding:1rem;">No history yet</p>', unsafe_allow_html=True)
    else:
        for idx, item in enumerate(st.session_state.prediction_history[:6]):
            st.markdown(f"""
            <div class="history-item">
                <span class="history-teams">{item['batting_team'][:3]} v {item['bowling_team'][:3]}</span>
                <span class="history-score">{item['predicted_score']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Load", key=f"load_{idx}", use_container_width=True):
                st.session_state.load_history_action = idx
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Stats Card with Progress Indicators
    if valid and st.session_state.show_prediction:
        # Calculate values upfront
        difficulty = min(100, max(0, int((1 - (crr / (required_rate + 0.1))) * 50 + 50))) if required_rate > 0 else 75
        
        st.markdown('<p class="card-header">Match Analysis</p>', unsafe_allow_html=True)
        
        # Stats in columns
        s1, s2 = st.columns(2)
        with s1:
            st.metric("Balls Left", balls_left)
        with s2:
            st.metric("Wickets In Hand", wickets_left)
        
        # Progress bars with labels
        st.caption(f"Overs: {overs}/20")
        st.progress(overs / 20)
        
        st.caption(f"Wickets: {wickets}/10")
        st.progress(wickets / 10)
        
        # Chase Confidence
        st.caption("Chase Confidence")
        st.progress(difficulty / 100)
        conf_color = '#10b981' if difficulty >= 50 else '#ef4444'
        st.markdown(f'<p style="text-align:center;font-size:1.5rem;font-weight:bold;color:{conf_color};margin:0;">{difficulty}%</p>', unsafe_allow_html=True)
