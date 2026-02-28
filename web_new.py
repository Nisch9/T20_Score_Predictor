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
    try:
        with open(HIST_FILE, 'w') as f:
            json.dump(st.session_state.prediction_history, f)
    except Exception:
        pass

# ── PREMIUM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --pitch:       #0d1f0f;
    --emerald:     #00c95d;
    --lime:        #39ff14;
    --gold:        #f5c842;
    --cream:       #fdf6e3;
    --slate:       #8a9ba8;
    --mist:        #c8d8e0;
    --red:         #ff3b3b;
    --card-bg:     rgba(10, 28, 12, 0.82);
    --card-border: rgba(0, 201, 93, 0.18);
}

html, body, .stApp {
    background: var(--pitch) !important;
    font-family: 'Outfit', sans-serif;
    color: var(--mist);
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(0,201,93,0.025) 40px, rgba(0,201,93,0.025) 41px),
        repeating-linear-gradient(90deg, transparent, transparent 60px, rgba(0,201,93,0.015) 60px, rgba(0,201,93,0.015) 61px),
        radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0,201,93,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 80% 100%, rgba(245,200,66,0.06) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

.block-container {
    padding: 1.2rem 2rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── HEADER ── */
.main-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.8rem;
    margin-bottom: 1.4rem;
    background: linear-gradient(135deg, rgba(0,201,93,0.15) 0%, rgba(10,28,12,0.95) 100%);
    border: 1px solid rgba(0,201,93,0.25);
    border-radius: 16px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '🏏';
    position: absolute;
    right: -20px; top: -20px;
    font-size: 8rem;
    opacity: 0.06;
    transform: rotate(30deg);
    line-height: 1;
}
.main-header::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, var(--emerald), var(--gold));
    border-radius: 4px 0 0 4px;
}
.main-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    letter-spacing: 3px;
    color: var(--cream);
    line-height: 1;
    margin: 0;
}
.main-subtitle {
    font-size: 0.72rem;
    color: var(--emerald);
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
    margin-top: 2px;
    margin-bottom: 0;
}
.header-badge {
    background: rgba(0,201,93,0.12);
    border: 1px solid rgba(0,201,93,0.3);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.7rem;
    color: var(--emerald);
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── GLASS CARD ── */
.glass-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.9rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,201,93,0.4), transparent);
}
.card-header {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--emerald);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,201,93,0.3), transparent);
}

/* ── MATCH DISPLAY ── */
.match-display {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.4rem 0;
}
.team-name {
    background: linear-gradient(135deg, rgba(0,201,93,0.2), rgba(0,201,93,0.08));
    border: 1px solid rgba(0,201,93,0.35);
    border-radius: 10px;
    padding: 0.5rem 1rem;
    flex: 1;
    text-align: center;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 2px;
    color: var(--cream);
}
.vs-badge {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem;
    color: var(--gold);
    letter-spacing: 2px;
    flex-shrink: 0;
}

/* ── BIG SCORE ── */
.big-score {
    text-align: center;
    padding: 0.4rem 0;
}
.score-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    line-height: 1;
    color: var(--cream);
    letter-spacing: 2px;
}
.score-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--gold);
    letter-spacing: 1px;
    margin-top: 2px;
}

/* ── PREDICTION BOX ── */
.prediction-box {
    position: relative;
    background: linear-gradient(135deg, #0b2e14 0%, #0d3318 50%, #0a1f0c 100%);
    border: 2px solid rgba(245,200,66,0.5);
    border-radius: 16px;
    padding: 1.4rem;
    text-align: center;
    overflow: hidden;
    margin-bottom: 0.9rem;
}
.prediction-box::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 50%, rgba(245,200,66,0.08) 0%, transparent 70%);
}
.prediction-box::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    opacity: 0.8;
}
.prediction-label {
    font-size: 0.62rem;
    color: var(--gold);
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0.3rem;
    position: relative;
}
.prediction-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    line-height: 1;
    color: var(--gold);
    letter-spacing: 4px;
    position: relative;
    text-shadow: 0 0 40px rgba(245,200,66,0.4);
}
.prediction-detail {
    font-size: 0.72rem;
    color: rgba(253,246,227,0.7);
    position: relative;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
    margin-top: 0.3rem;
}

/* ── HISTORY ITEMS ── */
.history-item {
    background: rgba(0,201,93,0.04);
    border: 1px solid rgba(0,201,93,0.15);
    border-radius: 10px;
    padding: 0.55rem 0.8rem;
    margin-bottom: 0.45rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.history-teams {
    font-size: 0.78rem;
    color: var(--mist);
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
}
.history-score {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    color: var(--gold);
    letter-spacing: 2px;
    line-height: 1;
}

/* ── FORM OVERRIDES ── */
.stSelectbox label, .stNumberInput label,
div[data-testid="stWidgetLabel"] {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--slate) !important;
    font-family: 'Outfit', sans-serif !important;
}
.stSelectbox > div > div,
.stNumberInput > div > div {
    background: rgba(6, 20, 8, 0.7) !important;
    border: 1px solid rgba(0,201,93,0.2) !important;
    border-radius: 8px !important;
    color: var(--cream) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
    border-radius: 8px !important;
    border: none !important;
    transition: all 0.2s ease !important;
    background: linear-gradient(135deg, #00c95d 0%, #00a34c 100%) !important;
    color: #0a1a0c !important;
    box-shadow: 0 4px 20px rgba(0,201,93,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(0,201,93,0.5) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: rgba(0,201,93,0.04) !important;
    border: 1px solid rgba(0,201,93,0.12) !important;
    border-radius: 10px !important;
    padding: 0.6rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.3rem !important;
    color: var(--emerald) !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.6rem !important;
    color: var(--slate) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

/* ── CAPTION / PROGRESS ── */
.stCaption {
    font-size: 0.62rem !important;
    color: var(--slate) !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--emerald), var(--lime)) !important;
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

# Header
st.markdown("""
<div class="main-header">
    <div>
        <p class="main-title">T20 Score Predictor</p>
        <p class="main-subtitle">Machine Learning · Cricket Intelligence</p>
    </div>
    <div class="header-badge">🟢 Model Ready</div>
</div>
""", unsafe_allow_html=True)

# Main Layout: 3 columns
col_form, col_result, col_history = st.columns([1.2, 1.3, 0.8])

# Helper: Hide prediction on any input change
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
        predict = st.button("⚡ Predict Score", use_container_width=True, type="primary")
    with b2:
        if st.button("Reset", use_container_width=True):
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
    if valid:
        # Match Display
        st.markdown(f"""
        <div class="glass-card">
            <p class="card-header">Match</p>
            <div class="match-display">
                <span class="team-name">{batting_team}</span>
                <span class="vs-badge">VS</span>
                <span class="team-name">{bowling_team}</span>
            </div>
            <p style="text-align:center;color:var(--slate);font-size:0.7rem;margin:0.4rem 0 0;letter-spacing:1px;text-transform:uppercase;">{city}</p>
        </div>
        """, unsafe_allow_html=True)

        # Current Score Display
        st.markdown(f"""
        <div class="glass-card">
            <p class="card-header">Live Score</p>
            <div class="big-score">
                <div class="score-value">{current_score}/{wickets}</div>
                <div class="score-info">{overs} overs &nbsp;·&nbsp; CRR: {crr:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Prediction Display
        if st.session_state.show_prediction and valid and predicted_score is not None:
            st.markdown(f"""
            <div class="prediction-box">
                <p class="prediction-label">✦ Predicted Final Score ✦</p>
                <p class="prediction-value">{predicted_score}</p>
                <p class="prediction-detail">+{runs_to_add} runs remaining &nbsp;·&nbsp; RRR: {required_rate:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            # Three charts
            with st.container():
                chart1, chart2, chart3 = st.columns([1, 1, 1])
                with chart1:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=crr,
                        title={'text': "Current RR", 'font': {'size': 11, 'color': '#8a9ba8'}},
                        number={'font': {'size': 22, 'color': '#00c95d'}},
                        gauge={
                            'axis': {'range': [0, 15], 'tickcolor': 'rgba(255,255,255,0.2)',
                                     'tickfont': {'color': '#8a9ba8', 'size': 7}},
                            'bar': {'color': '#00c95d', 'thickness': 0.25},
                            'bgcolor': 'rgba(0,0,0,0)',
                            'borderwidth': 0,
                            'steps': [
                                {'range': [0, 6],   'color': 'rgba(255,59,59,0.15)'},
                                {'range': [6, 10],  'color': 'rgba(245,200,66,0.15)'},
                                {'range': [10, 15], 'color': 'rgba(0,201,93,0.15)'}
                            ],
                            'threshold': {
                                'line': {'color': '#f5c842', 'width': 3},
                                'thickness': 0.8,
                                'value': required_rate
                            }
                        }
                    ))
                    fig_gauge.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#c8d8e0'},
                        height=180,
                        margin=dict(l=10, r=10, t=35, b=5)
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

                with chart2:
                    percent_complete = int(current_score / predicted_score * 100) if predicted_score else 0
                    fig_donut = go.Figure(data=[go.Pie(
                        labels=['Scored', 'To Add'],
                        values=[current_score, max(0, runs_to_add)],
                        hole=0.65,
                        marker=dict(
                            colors=['#00c95d', 'rgba(255,255,255,0.05)'],
                            line=dict(color='rgba(0,0,0,0)', width=0)
                        ),
                        textinfo='none',
                        hovertemplate='%{label}: %{value}<extra></extra>'
                    )])
                    fig_donut.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#c8d8e0'},
                        height=180,
                        margin=dict(l=10, r=10, t=10, b=10),
                        showlegend=False,
                        annotations=[{
                            'text': f'<b>{percent_complete}%</b><br><span style="font-size:9px">Complete</span>',
                            'x': 0.5, 'y': 0.5,
                            'font_size': 16,
                            'font_color': '#00c95d',
                            'showarrow': False
                        }]
                    )
                    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

                with chart3:
                    conservative = int(predicted_score * 0.92)
                    aggressive = int(predicted_score * 1.08)
                    fig_bar = go.Figure(data=[go.Bar(
                        x=['Conservative', 'Predicted', 'Aggressive'],
                        y=[conservative, predicted_score, aggressive],
                        marker=dict(
                            color=['rgba(255,59,59,0.8)', 'rgba(0,201,93,0.9)', 'rgba(59,130,246,0.8)'],
                            line=dict(width=0)
                        ),
                        text=[conservative, predicted_score, aggressive],
                        textposition='outside',
                        textfont={'color': '#c8d8e0', 'size': 10},
                        width=0.5
                    )])
                    fig_bar.update_layout(
                        title={'text': 'Score Projections', 'font': {'color': '#8a9ba8', 'size': 11}, 'x': 0.5},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#c8d8e0'},
                        height=180,
                        margin=dict(l=10, r=10, t=35, b=25),
                        yaxis={'visible': False, 'range': [0, aggressive * 1.18]},
                        xaxis={'tickfont': {'size': 8, 'color': '#8a9ba8'}},
                        bargap=0.4
                    )
                    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:2.5rem 2rem;">
                <p style="font-size:2.5rem;margin:0;opacity:0.4;">⚡</p>
                <p style="color:var(--slate);margin:0.5rem 0 0;font-size:0.88rem;">Click <strong style="color:var(--emerald);">Predict Score</strong> to see results</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3.5rem 2rem;">
            <p style="font-size:3rem;margin:0;opacity:0.3;">🏏</p>
            <p style="color:var(--slate);font-size:0.95rem;margin:0.6rem 0 0;">Select teams, venue and enter match details</p>
            <p style="color:rgba(138,155,168,0.5);font-size:0.75rem;margin-top:0.3rem;">Minimum 5 overs required</p>
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
        st.markdown('<p style="color:rgba(138,155,168,0.5);font-size:0.75rem;text-align:center;padding:1rem 0;">No history yet</p>', unsafe_allow_html=True)
    else:
        for idx, item in enumerate(st.session_state.prediction_history[:6]):
            st.markdown(f"""
            <div class="history-item">
                <span class="history-teams">{item['batting_team'][:3].upper()} v {item['bowling_team'][:3].upper()}</span>
                <span class="history-score">{item['predicted_score']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Load", key=f"load_{idx}", use_container_width=True):
                st.session_state.load_history_action = idx
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Stats Card with Progress Indicators
    if valid and st.session_state.show_prediction:
        difficulty = min(100, max(0, int((1 - (crr / (required_rate + 0.1))) * 50 + 50))) if required_rate > 0 else 75

        st.markdown('<p class="card-header">Match Analysis</p>', unsafe_allow_html=True)

        s1, s2 = st.columns(2)
        with s1:
            st.metric("Balls Left", balls_left)
        with s2:
            st.metric("Wickets In Hand", wickets_left)

        st.caption(f"Overs: {overs}/20")
        st.progress(overs / 20)

        st.caption(f"Wickets: {wickets}/10")
        st.progress(wickets / 10)

        st.caption("Chase Confidence")
        st.progress(difficulty / 100)
        conf_color = '#00c95d' if difficulty >= 50 else '#ff3b3b'
        st.markdown(f'<p style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;letter-spacing:2px;color:{conf_color};margin:0;">{difficulty}%</p>', unsafe_allow_html=True)