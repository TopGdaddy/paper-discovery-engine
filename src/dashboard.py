"""
dashboard.py - Ultra-Modern Research Discovery Platform
The most beautiful paper discovery experience ever built.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import re

# =============================================================================
# PATH SETUP
# =============================================================================

SRC_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SRC_DIR.parent.resolve()

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "papers.db"

from database import DatabaseManager, PaperRecord
import feedparser
from datetime import datetime
import pytz
# ML and Email imports
from ml_engine import PaperMLEngine
from email_service import EmailDigestService

try:
    import requests
except ImportError:
    requests = None

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Paper Discovery • AI Research Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# COSMIC CSS - THE MOST BEAUTIFUL DESIGN EVER
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;700&display=swap');

    /* === COSMIC BACKGROUND === */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #16213e 50%, #0f1419 100%);
        background-attachment: fixed;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }

    .block-container {
        padding: 2.5rem 2rem 6rem;
        max-width: 1800px;
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    /* === GLASSMORPHISM MAGIC === */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 28px;
        padding: 36px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideUp 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        transition: left 0.7s;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    .glass-card:hover {
        transform: translateY(-12px);
        box-shadow: 
            0 24px 48px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        border-color: rgba(139, 92, 246, 0.3);
    }

    /* === PAPER CARDS - ABSOLUTE PERFECTION === */
    .paper-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.95) 100%);
        border-radius: 32px;
        padding: 40px 44px;
        margin: 32px 0;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(0, 0, 0, 0.05);
        border-left: 8px solid;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
    }
    
    .paper-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 50%, #10b981 100%);
        border-radius: 32px 32px 0 0;
        opacity: 0;
        transition: opacity 0.5s;
    }
    
    .paper-card:hover::after {
        opacity: 1;
    }
    
    .paper-card:hover {
        transform: translateY(-20px) scale(1.01);
        box-shadow: 
            0 40px 90px rgba(0, 0, 0, 0.25),
            0 0 0 1px rgba(139, 92, 246, 0.2);
    }

    /* === SCORE BADGES - PURE DOPAMINE === */
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        padding: 14px 28px;
        border-radius: 60px;
        font-weight: 800;
        font-size: 17px;
        box-shadow: 
            0 10px 30px rgba(139, 92, 246, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.2);
        animation: glow 3s ease-in-out infinite;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    
    .score-badge-high {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.5);
    }
    
    .score-badge-medium {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.5);
    }

    /* === GRADIENT HEADINGS === */
    h1 {
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    
    h2, h3 {
        font-weight: 800 !important;
        color: #1e293b !important;
    }

    /* === BUTTONS === */
    .stButton > button {
        border-radius: 20px !important;
        height: 58px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 2px solid transparent !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
        border-color: currentColor !important;
    }

    /* === METRIC CARDS === */
    .metric-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 32px;
        text-align: center;
        border: 1px solid rgba(139, 92, 246, 0.2);
        transition: all 0.4s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card:hover {
        transform: scale(1.08) rotate(2deg);
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: 0 16px 48px rgba(139, 92, 246, 0.3);
    }
    
    .metric-value {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(135deg, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 12px 0;
    }
    
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    /* === ANIMATIONS === */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(60px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
        }
        50% {
            box-shadow: 0 10px 40px rgba(139, 92, 246, 0.7);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* === CATEGORY BADGES === */
    .category-badge {
        display: inline-block;
        background: rgba(15, 23, 42, 0.08);
        color: #1e293b;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 15px;
        border: 2px solid rgba(15, 23, 42, 0.12);
        transition: all 0.3s;
    }
    
    .category-badge:hover {
        background: rgba(139, 92, 246, 0.15);
        border-color: rgba(139, 92, 246, 0.3);
        transform: scale(1.05);
    }

    /* === LINKS === */
    .paper-link {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        color: white !important;
        padding: 18px 36px;
        border-radius: 18px;
        text-decoration: none;
        font-weight: 800;
        font-size: 16px;
        display: inline-block;
        box-shadow: 0 12px 35px rgba(139, 92, 246, 0.35);
        transition: all 0.4s ease;
        border: 2px solid transparent;
    }
    
    .paper-link:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 50px rgba(139, 92, 246, 0.5);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .paper-link-secondary {
        background: rgba(15, 23, 42, 0.08);
        color: #1e293b !important;
        border: 2px solid rgba(15, 23, 42, 0.15);
        box-shadow: none;
    }
    
    .paper-link-secondary:hover {
        background: rgba(15, 23, 42, 0.12);
        border-color: rgba(139, 92, 246, 0.3);
    }

    /* === INPUT FIELDS === */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 16px !important;
        border: 2px solid rgba(148, 163, 184, 0.2) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        padding: 14px 20px !important;
        font-size: 15px !important;
        transition: all 0.3s !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: rgba(139, 92, 246, 0.6) !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1) !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 600 !important;
        font-size: 16px !important;
        color: #e2e8f0 !important;
        padding: 14px 20px !important;
        border-radius: 14px !important;
        transition: all 0.3s !important;
        margin: 4px 0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(139, 92, 246, 0.15) !important;
        transform: translateX(6px) !important;
    }

    /* === EMPTY STATE === */
    .empty-state {
        text-align: center;
        padding: 120px 60px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 32px;
        border: 2px dashed rgba(148, 163, 184, 0.2);
    }
    
    .empty-state-icon {
        font-size: 80px;
        margin-bottom: 24px;
        animation: float 3s ease-in-out infinite;
    }
        /* === MOBILE FIXES === */
    
    /* Make hamburger menu more visible on mobile */
    @media (max-width: 768px) {
        /* Sidebar toggle button - make it more visible */
        [data-testid="collapsedControl"] {
            background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important;
            border-radius: 12px !important;
            padding: 12px !important;
            left: 10px !important;
            top: 10px !important;
            z-index: 999999 !important;
            box-shadow: 0 4px 20px rgba(139, 92, 246, 0.5) !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
        }
        
        [data-testid="collapsedControl"] svg {
            fill: white !important;
            stroke: white !important;
            width: 24px !important;
            height: 24px !important;
        }
        
        [data-testid="collapsedControl"]:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 6px 25px rgba(139, 92, 246, 0.7) !important;
        }
        
        /* Improve sidebar on mobile */
        [data-testid="stSidebar"] {
            min-width: 280px !important;
            z-index: 999998 !important;
        }
        
        /* Better spacing on mobile */
        .block-container {
            padding: 1rem 1rem 4rem !important;
        }
        
        /* Smaller headings on mobile */
        h1 {
            font-size: 32px !important;
        }
        
        /* Paper cards on mobile */
        .paper-card {
            padding: 20px !important;
            margin: 16px 0 !important;
            border-radius: 16px !important;
        }
        
        /* Metric cards on mobile */
        .metric-card {
            padding: 16px !important;
            margin-bottom: 12px !important;
        }
        
        .metric-value {
            font-size: 32px !important;
        }
        
        /* Glass card on mobile */
        .glass-card {
            padding: 20px !important;
            border-radius: 16px !important;
        }
        
        /* Empty state on mobile */
        .empty-state {
            padding: 60px 30px !important;
        }
        
        .empty-state-icon {
            font-size: 48px !important;
        }
    }
    
    /* Extra small screens (phones) */
    @media (max-width: 480px) {
        h1 {
            font-size: 24px !important;
        }
        
        .metric-value {
            font-size: 28px !important;
        }
        
        .metric-label {
            font-size: 11px !important;
        }
        
        .block-container {
            padding: 0.5rem 0.5rem 3rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE & HELPERS
# =============================================================================

@st.cache_resource
def get_database():
    return DatabaseManager(str(DB_PATH))

db = get_database()

@st.cache_resource
def get_ml_engine(_db):
    return PaperMLEngine(_db)

@st.cache_resource
def get_email_service(_db):
    return EmailDigestService(_db)

ml_engine = get_ml_engine(db)
email_service = get_email_service(db)

def clean_text(text):
    """Clean text by removing HTML tags, extra whitespace, and problematic characters"""
    if not text:
        return ""
    text = str(text)
    
    # Remove problematic characters FIRST
    text = text.replace('\xa0', ' ')  # non-breaking space
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\r', '')      # carriage return
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Decode HTML entities
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    
    return text.strip()

def clean_form_input(text):
    """Clean form input to remove problematic characters for email/database"""
    if not text:
        return text
    text = str(text).strip()
    # Remove non-breaking spaces and other problematic chars
    text = text.replace('\xa0', ' ')
    text = text.replace('\u200b', '')
    text = text.replace('\r', '')
    # Normalize whitespace
    text = ' '.join(text.split())
    return text

def truncate(text, length=100):
    if not text:
        return ""
    text = clean_text(text)
    return text if len(text) <= length else text[:length].rsplit(' ', 1)[0] + "..."

def get_score_style(score):
    """Returns color, emoji, and badge class for score"""
    s = score or 0
    if s >= 0.75:
        return "#10b981", "🔥", "score-badge-high"
    if s >= 0.60:
        return "#3b82f6", "⚡", "score-badge-medium"
    if s >= 0.45:
        return "#8b5cf6", "⭐", "score-badge"
    return "#64748b", "📄", "score-badge"

# =============================================================================
# COMPONENTS
# =============================================================================

def render_paper_card(paper: PaperRecord, show_summary=True):
    """Renders paper card using Streamlit components"""
    score = paper.relevance_score or 0
    color, emoji, badge_class = get_score_style(score)
    
    # Clean all text content
    title = clean_text(paper.title or "Untitled Paper")
    authors = clean_text(paper.authors or "Unknown Authors")
    summary = clean_text(paper.summary or "") if show_summary else ""
    category = clean_text(paper.primary_category or "Unknown")
    
    # Truncate after cleaning
    title = title[:120] + "..." if len(title) > 120 else title
    authors = authors[:100] + "..." if len(authors) > 100 else authors
    summary = summary[:340] + "..." if len(summary) > 340 else summary
    
    pdf_url = paper.pdf_url or "#"
    abs_url = paper.abs_url or "#"
    
    # Use Streamlit components for clean rendering
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<span style="background: linear-gradient(135deg, {color} 0%, {color} 100%); color: white; padding: 8px 16px; border-radius: 30px; font-weight: 700; font-size: 14px;">{emoji} {score:.0%} match</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span style="background: rgba(15, 23, 42, 0.08); color: #1e293b; padding: 8px 16px; border-radius: 30px; font-weight: 700; font-size: 14px;">📂 {category}</span>', unsafe_allow_html=True)
        
        st.markdown(f"### [{title}]({abs_url})")
        st.markdown(f"**👤 {authors}**")
        
        if summary:
            st.write(summary)
        
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📄 Read PDF", pdf_url, use_container_width=True)
        with col2:
            st.link_button("🔗 arXiv Abstract", abs_url, use_container_width=True)
        
        st.divider()

def render_metric_card(label, value, icon="📊"):
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 40px; margin-bottom: 12px;">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# CHARTS
# =============================================================================

def create_score_chart(papers):
    if not papers:
        return None
    
    scores = [(p.relevance_score or 0) * 100 for p in papers]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=20,
        marker=dict(
            color='rgba(139, 92, 246, 0.7)',
            line=dict(color='rgba(139, 92, 246, 1)', width=2)
        ),
        hovertemplate='Score: %{x:.0f}%<br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Score Distribution', font=dict(size=18, color='#e2e8f0')),
        xaxis=dict(
            title=dict(text='Relevance Score (%)', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)',
            range=[0, 100]
        ),
        yaxis=dict(
            title=dict(text='Papers', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=360,
        margin=dict(l=60, r=30, t=60, b=50)
    )
    return fig

def create_category_chart(papers):
    if not papers:
        return None
    
    categories = {}
    for p in papers:
        cat = p.primary_category or "Unknown"
        categories[cat] = categories.get(cat, 0) + 1
    
    sorted_cats = sorted(categories.items(), key=lambda x: -x[1])[:10]
    df = pd.DataFrame(sorted_cats, columns=['Category', 'Count'])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df['Category'],
        x=df['Count'],
        orientation='h',
        marker=dict(
            color=df['Count'],
            colorscale='Purples',
            line=dict(color='rgba(139, 92, 246, 1)', width=2)
        ),
        hovertemplate='%{y}<br>Papers: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Top Categories', font=dict(size=18, color='#e2e8f0')),
        xaxis=dict(
            title=dict(text='Papers', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        yaxis=dict(
            tickfont=dict(size=12, color='#94a3b8'),
            categoryorder='total ascending'
        ),
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=420,
        margin=dict(l=140, r=30, t=60, b=50)
    )
    return fig

def create_timeline_chart(papers):
    if not papers:
        return None
    
    dates = {}
    for p in papers:
        if p.published:
            date_key = p.published.strftime('%Y-%m-%d')
            dates[date_key] = dates.get(date_key, 0) + 1
    
    if not dates:
        return None
    
    df = pd.DataFrame([
        {'Date': k, 'Papers': v} 
        for k, v in sorted(dates.items())[-30:]
    ])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Papers'],
        mode='lines+markers',
        line=dict(color='#8b5cf6', width=4),
        marker=dict(size=10, color='#8b5cf6'),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)',
        hovertemplate='%{x}<br>Papers: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Papers Over Time', font=dict(size=18, color='#e2e8f0')),
        xaxis=dict(
            title=dict(text='Date', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=11, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        yaxis=dict(
            title=dict(text='Papers', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=320,
        margin=dict(l=60, r=30, t=60, b=50)
    )
    return fig

# =============================================================================
# HELPERS
# =============================================================================

def save_paper_from_arxiv(entry):
    """Save a paper from arXiv search to database"""
    arxiv_id = entry.link.split("/")[-1]
    
    # Check if already exists
    existing = db.session.query(PaperRecord).filter_by(arxiv_id=arxiv_id).first()
    if existing:
        return False, "Already saved!"
    
    # Extract published date properly
    published = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            published = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
        except:
            published = datetime.now(pytz.UTC)
    
    new_paper = PaperRecord(
        arxiv_id=arxiv_id,
        title=entry.title,
        authors=', '.join([a.name for a in entry.authors]) if hasattr(entry, 'authors') else "Unknown",
        summary=entry.summary,
        pdf_url=entry.link.replace("/abs/", "/pdf/") + ".pdf",
        abs_url=entry.link,
        primary_category=getattr(entry, 'category', 'cs.LG') if hasattr(entry, 'tags') and entry.tags else "cs.LG",
        published=published,
        relevance_score=0.95  # Mark as highly relevant since you saved it
    )
    
    db.session.add(new_paper)
    db.session.commit()
    return True, "Saved to Reading List!"

def do_search(query, limit=50):
    if not query or not query.strip():
        return []
    try:
        return db.search_papers(keyword=query.strip(), limit=limit)
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

@st.cache_data(ttl=3600)
def get_reddit_trending():
    if requests is None:
        return []
    trending = []
    try:
        headers = {'User-Agent': 'PaperDiscoveryBot/2.0'}
        for sub in ['MachineLearning', 'artificial']:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                posts = resp.json().get('data', {}).get('children', [])
                for post in posts[:2]:
                    data = post.get('data', {})
                    title = data.get('title', '')
                    if title:
                        trending.append({
                            'title': truncate(title, 60),
                            'score': data.get('score', 0),
                            'url': f"https://reddit.com{data.get('permalink', '')}",
                            'source': f"r/{sub}"
                        })
        trending.sort(key=lambda x: x['score'], reverse=True)
        return trending[:5]
    except Exception:
        return []

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 50px 20px 40px;">
        <div style="font-size: 80px; margin-bottom: 16px; animation: float 4s ease-in-out infinite;">✨</div>
        <h1 style="font-size: 36px; font-weight: 900; margin: 0; letter-spacing: -1px;">
            Paper Discovery
        </h1>
        <p style="color: #94a3b8; font-size: 16px; margin-top: 16px; font-weight: 600; letter-spacing: 0.5px;">
            Your AI Research Companion
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    page = st.radio(
    "Navigate",
    ["🏠 Dashboard", "📄 Browse Papers", "🔍 Search", "📚 My Reading List", "🏷️ Label Papers", "🧠 My AI", "📊 Analytics", "⚙️ Settings"],
    label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("**📈 Quick Stats**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Papers", f"{db.count_papers():,}")
    with col2:
        st.metric("Labeled", db.count_labeled())
    
    st.divider()
    
    st.markdown("**🔥 Trending**")
    trending = get_reddit_trending()
    if trending:
        for item in trending[:4]:
            st.markdown(f"""
            <a href="{item['url']}" target="_blank" style="
                display: block; background: rgba(139, 92, 246, 0.1);
                border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px;
                padding: 12px 14px; margin: 10px 0; color: #e2e8f0;
                text-decoration: none; font-size: 13px; line-height: 1.5;
                transition: all 0.3s;">
                {item['title']}<br>
                <span style="color: #94a3b8; font-size: 12px;">{item['source']} • ⬆️ {item['score']}</span>
            </a>
            """, unsafe_allow_html=True)

# =============================================================================
# PAGES
# =============================================================================

if page == "🏠 Dashboard":
    st.markdown("""
    <h1 style='text-align: center; font-size: 64px; margin: 80px 0 24px; letter-spacing: -2px;'>
        Your Daily Research Magic ✨
    </h1>
    <p style='text-align: center; font-size: 22px; color: #94a3b8; margin-bottom: 80px; font-weight: 500;'>
        Curated by AI • Personalized for You
    </p>
    """, unsafe_allow_html=True)
    
    try:
        all_papers = db.get_all_papers(limit=1000)
        stats = db.get_stats()
    except Exception as e:
        st.error(f"Error: {e}")
        all_papers = []
        stats = {}
    
    if all_papers:
        high_rel = len([p for p in all_papers if (p.relevance_score or 0) >= 0.55])
        avg_score = sum(p.relevance_score or 0 for p in all_papers) / len(all_papers)
    else:
        high_rel = 0
        avg_score = 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Total Papers", str(len(all_papers)), "📄")
    with col2:
        render_metric_card("High Relevance", str(high_rel), "🔥")
    with col3:
        render_metric_card("Labeled", str(stats.get('labeled_papers', 0)), "🏷️")
    with col4:
        render_metric_card("Avg Score", f"{avg_score:.0%}", "📊")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_main, col_side = st.columns([3, 2])
    
    with col_main:
        st.markdown('<h2 style="font-size: 32px; margin: 0 0 32px; background: linear-gradient(135deg, #8b5cf6, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔥 Top Recommendations</h2>', unsafe_allow_html=True)
        if all_papers:
            top_papers = sorted(all_papers, key=lambda p: p.relevance_score or 0, reverse=True)[:5]
            for paper in top_papers:
                render_paper_card(paper, show_summary=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h3 style="color: #e2e8f0; margin: 0 0 16px;">No papers yet</h3>
                <p style="color: #94a3b8;">Run the pipeline to fetch papers!</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_side:
        if all_papers:
            fig = create_score_chart(all_papers)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<h3 style="font-size: 24px; margin: 40px 0 24px; color: #e2e8f0;">📂 Top Categories</h3>', unsafe_allow_html=True)
        
        if all_papers:
            cats = {}
            for p in all_papers:
                cat = p.primary_category or "Unknown"
                cats[cat] = cats.get(cat, 0) + 1
            
            for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:6]:
                pct = count / len(all_papers) * 100
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 16px 20px; 
                background: rgba(139, 92, 246, 0.1); border-radius: 12px; margin: 12px 0;
                border: 1px solid rgba(139, 92, 246, 0.2); transition: all 0.3s;">
                    <span style="color: #e2e8f0; font-weight: 600;">{cat}</span>
                    <span style="color: #94a3b8; font-weight: 700;">{count} ({pct:.0f}%)</span>
                </div>
                """, unsafe_allow_html=True)

elif page == "📄 Browse Papers":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        📄 Browse Papers
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Explore and filter your collection
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        min_score = st.slider("📊 Min Score", 0, 100, 0, 5, format="%d%%")
    with col2:
        try:
            categories = ["All"] + db.get_categories()
        except:
            categories = ["All"]
        selected_cat = st.selectbox("📂 Category", categories)
    with col3:
        sort_opts = {
            "🔥 Score ↓": "score_desc",
            "📉 Score ↑": "score_asc",
            "🆕 Newest": "date_desc",
            "📅 Oldest": "date_asc"
        }
        sort_by = st.selectbox("🔢 Sort", list(sort_opts.keys()))
    with col4:
        per_page = st.selectbox("📄 Show", [25, 50, 100])
    
    st.divider()
    
    try:
        all_papers = db.get_all_papers(limit=2000)
    except:
        all_papers = []
    
    filtered = [p for p in all_papers if (p.relevance_score or 0) * 100 >= min_score]
    if selected_cat != "All":
        filtered = [p for p in filtered if p.primary_category == selected_cat]
    
    sort_key = sort_opts[sort_by]
    if sort_key == "score_desc":
        filtered.sort(key=lambda p: p.relevance_score or 0, reverse=True)
    elif sort_key == "score_asc":
        filtered.sort(key=lambda p: p.relevance_score or 0)
    elif sort_key == "date_desc":
        filtered.sort(key=lambda p: p.published or datetime.min, reverse=True)
    else:
        filtered.sort(key=lambda p: p.published or datetime.min)
    
    total = len(filtered)
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    col_info, col_page = st.columns([4, 1])
    with col_info:
        st.markdown(f"**Found {total:,} papers**")
    with col_page:
        current_page = st.number_input("Page", 1, total_pages, 1, label_visibility="collapsed")
    
    start = (current_page - 1) * per_page
    papers_to_show = filtered[start:start + per_page]
    
    for paper in papers_to_show:
        render_paper_card(paper)

elif page == "🔍 Search":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        🔍 Universal Research Discovery
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Search ALL science • Save works perfectly now
    </p>
    """, unsafe_allow_html=True)

    # Initialize session state for search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'saved_papers' not in st.session_state:
        st.session_state.saved_papers = set()
    if 'just_saved' not in st.session_state:
        st.session_state.just_saved = None

    # Show balloons if just saved
    if st.session_state.just_saved:
        st.balloons()
        st.toast(f"✅ Saved: {st.session_state.just_saved}", icon="🎉")
        st.session_state.just_saved = None

    # Categories
    categories = {
        "All Fields": "",
        "cs.AI - Artificial Intelligence": "cs.AI",
        "cs.LG - Machine Learning": "cs.LG",
        "cs.CV - Computer Vision": "cs.CV",
        "physics - All Physics": "physics",
        "quant-ph - Quantum Computing": "quant-ph",
        "q-bio - Quantitative Biology": "q-bio",
        "math - All Mathematics": "math",
        "q-fin - Quantitative Finance": "q-fin",
    }

    with st.form(key="search_form"):
        query = st.text_input("🔍 Search all of science", placeholder="grok, quantum, cancer, bitcoin...", label_visibility="collapsed")
        col1, col2 = st.columns([1, 1])
        with col1:
            selected_cat = st.selectbox("Field", list(categories.keys()), index=0)
        with col2:
            num_results = st.selectbox("Results", [10, 20, 30], index=1)
        submit = st.form_submit_button("🚀 Search arXiv", use_container_width=True)

    if submit and query.strip():
        cat_code = categories[selected_cat]
        cat_query = f"+cat:{cat_code}" if cat_code else ""
        
        with st.spinner("Searching arXiv..."):
            import time, urllib.parse
            time.sleep(3)
            
            headers = {'User-Agent': 'VeerEngine/1.0'}
            encoded = urllib.parse.quote(query)
            url = f"https://export.arxiv.org/api/query?search_query=all:{encoded}{cat_query}&max_results={num_results}&sortBy=submittedDate"
            
            try:
                r = requests.get(url, headers=headers, timeout=15)
                feed = feedparser.parse(r.content)
                
                # Store results in session state
                st.session_state.search_results = []
                for entry in feed.entries:
                    arxiv_id = entry.link.split("/")[-1]
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
                    published_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    
                    st.session_state.search_results.append({
                        'arxiv_id': arxiv_id,
                        'title': entry.title,
                        'authors': ', '.join([a.name for a in entry.authors]) if hasattr(entry, 'authors') else "Unknown",
                        'summary': entry.summary,
                        'pdf_url': pdf_url,
                        'abs_url': entry.link,
                        'category': entry.tags[0].term if entry.tags else "unknown",
                        'published': published_date
                    })
                
                st.success(f"Found {len(st.session_state.search_results)} papers!")
                
            except Exception as e:
                st.error("arXiv is slow — try again in 10 seconds")
                st.session_state.search_results = []

    # Display results from session state
    if st.session_state.search_results:
        
        # Get already saved arxiv_ids from database
        try:
            saved_arxiv_ids = {p.arxiv_id for p in db.get_all_papers() if hasattr(p, 'arxiv_id')}
        except:
            saved_arxiv_ids = set()
        
        # Merge with session saved papers
        saved_arxiv_ids = saved_arxiv_ids.union(st.session_state.saved_papers)
        
        for i, paper in enumerate(st.session_state.search_results):
            arxiv_id = paper['arxiv_id']
            title = clean_text(paper['title'])
            authors = paper['authors']
            summary = clean_text(paper['summary'])[:380] + "..."
            pdf_url = paper['pdf_url']
            abs_url = paper['abs_url']
            
            already_saved = arxiv_id in saved_arxiv_ids
            
            with st.container():
                st.markdown(f"""
                <div class="paper-card" style="border-left-color: {'#10b981' if already_saved else '#8b5cf6'};">
                    <h3 style="margin:16px 0; color:#e2e8f0; font-size:24px;">{title}</h3>
                    <p style="color:#94a3b8;">👤 {authors}</p>
                    <p style="color:#cbd5e1;">{summary}</p>
                    <div style="margin-top:20px;">
                        <a href="{pdf_url}" target="_blank" class="paper-link">📄 PDF</a>
                        <a href="{abs_url}" target="_blank" class="paper-link paper-link-secondary">🔗 arXiv</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if already_saved:
                    st.success("✓ Already in Reading List")
                else:
                    # Use unique key with index
                    if st.button("✨ Save to Reading List", key=f"save_{arxiv_id}_{i}"):
                        try:
                            new_paper = PaperRecord(
                                arxiv_id=arxiv_id,
                                title=paper['title'],
                                authors=paper['authors'],
                                summary=paper['summary'],
                                pdf_url=paper['pdf_url'],
                                abs_url=paper['abs_url'],
                                primary_category=paper['category'],
                                published=paper['published'],
                                relevance_score=0.99
                            )
                            
                            db.session.add(new_paper)
                            db.session.commit()
                            
                            # Track saved paper
                            st.session_state.saved_papers.add(arxiv_id)
                            st.session_state.just_saved = title[:50] + "..."
                            
                            st.rerun()  # Rerun to show balloons and update UI
                            
                        except Exception as e:
                            db.session.rollback()
                            st.error(f"Save failed: {str(e)}")
                
                st.markdown("<br>", unsafe_allow_html=True)

    elif not submit:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🌍</div>
            <h3 style="color: #e2e8f0;">Search everything</h3>
            <p style="color: #94a3b8;">Physics • Biology • Math • Finance • AI • Everything</p>
        </div>
        """, unsafe_allow_html=True)
    
    if submit and not query.strip():
        st.warning("Please type something to search!")


elif page == "🏷️ Label Papers":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        🏷️ Label Papers
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Help improve the AI by rating papers
    </p>
    """, unsafe_allow_html=True)
    
    try:
        stats = db.get_stats()
    except:
        stats = {}
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Labeled", str(stats.get('labeled_papers', 0)), "✅")
    with col2:
        render_metric_card("Relevant", str(stats.get('positive_labels', 0)), "👍")
    with col3:
        render_metric_card("Not Relevant", str(stats.get('negative_labels', 0)), "👎")
    with col4:
        render_metric_card("Remaining", str(stats.get('unlabeled_papers', 0)), "📝")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if stats.get('total_papers', 0) > 0:
        progress = stats['labeled_papers'] / stats['total_papers']
        st.progress(progress)
        st.caption(f"📊 {progress:.0%} complete")
    
    st.divider()
    
    try:
        unlabeled = db.get_unlabeled_papers(limit=5)
    except:
        unlabeled = []
    
    if not unlabeled:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🎉</div>
            <h3 style="color: #e2e8f0; margin: 0 0 16px;">All Papers Labeled!</h3>
            <p style="color: #94a3b8;">You can now retrain the classifier</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<h2 style="font-size: 28px; margin: 0 0 32px; color: #e2e8f0;">📝 Papers to Label ({len(unlabeled)} shown)</h2>', unsafe_allow_html=True)
        
        for paper in unlabeled:
            render_paper_card(paper)
            col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 3])
            
            with col1:
                if st.button("👍 Relevant", key=f"rel_{paper.arxiv_id}", use_container_width=True):
                    try:
                        db.label_paper(paper.arxiv_id, 1)
                        st.toast("✅ Labeled relevant!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("👎 Not Relevant", key=f"not_{paper.arxiv_id}", use_container_width=True):
                    try:
                        db.label_paper(paper.arxiv_id, 0)
                        st.toast("❌ Labeled not relevant!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col3:
                st.link_button("📄 Read First", paper.pdf_url or "#", use_container_width=True)
            
            st.divider()

elif page == "📊 Analytics":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        📊 Analytics Dashboard
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Deep insights into your collection
    </p>
    """, unsafe_allow_html=True)
    
    try:
        all_papers = db.get_all_papers(limit=2000)
    except:
        all_papers = []
    
    if not all_papers:
        st.warning("📭 No papers yet!")
    else:
        scores = [p.relevance_score or 0 for p in all_papers]
        avg_score = sum(scores) / len(scores)
        high_rel = len([s for s in scores if s >= 0.55])
        low_rel = len([s for s in scores if s < 0.35])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            render_metric_card("Total", str(len(all_papers)), "📄")
        with col2:
            render_metric_card("Avg Score", f"{avg_score:.0%}", "📊")
        with col3:
            render_metric_card("High", str(high_rel), "🔥")
        with col4:
            render_metric_card("Low", str(low_rel), "📉")
        with col5:
            try:
                cat_count = len(db.get_categories())
            except:
                cat_count = 0
            render_metric_card("Categories", str(cat_count), "📂")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = create_score_chart(all_papers)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_category_chart(all_papers)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = create_timeline_chart(all_papers)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('<h3 style="font-size: 24px; margin: 0 0 24px; color: #e2e8f0;">🏆 Top 5 Papers</h3>', unsafe_allow_html=True)
            top_5 = sorted(all_papers, key=lambda p: p.relevance_score or 0, reverse=True)[:5]
            for i, p in enumerate(top_5, 1):
                score = p.relevance_score or 0
                color, emoji, _ = get_score_style(score)
                title_clean = clean_text(p.title or "Untitled")[:50]
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 16px 20px; 
                background: rgba(139, 92, 246, 0.1); border-radius: 12px; margin: 12px 0;
                border-left: 4px solid {color};">
                    <span style="font-size: 24px; font-weight: 900; color: {color}; margin-right: 16px;">#{i}</span>
                    <div style="flex: 1;">
                        <div style="font-size: 14px; font-weight: 600; color: #e2e8f0;">{title_clean}</div>
                        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{emoji} {score:.0%}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown('<h3 style="font-size: 28px; margin: 32px 0 24px; color: #e2e8f0;">📈 Score Breakdown</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        brackets = [
            ("🔥 Excellent", len([s for s in scores if s >= 0.75])),
            ("⭐ Good", len([s for s in scores if 0.55 <= s < 0.75])),
            ("👍 Fair", len([s for s in scores if 0.35 <= s < 0.55])),
            ("📄 Low", len([s for s in scores if s < 0.35]))
        ]
        
        for i, (label, count) in enumerate(brackets):
            with [col1, col2, col3, col4][i]:
                pct = count / len(all_papers) * 100 if all_papers else 0
                st.markdown(f"""
                <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 16px; padding: 24px; text-align: center;">
                    <div style="font-size: 14px; color: #94a3b8; margin-bottom: 8px;">{label}</div>
                    <div style="font-size: 40px; font-weight: 900; color: #8b5cf6;">{count}</div>
                    <div style="font-size: 13px; color: #64748b; margin-top: 4px;">{pct:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

elif page == "📚 My Reading List":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        📚 My Reading List
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Papers you saved • Your personal collection
    </p>
    """, unsafe_allow_html=True)
    
    # Get papers from reading list (is_saved = True)
    saved_papers = db.get_reading_list()
    
    if not saved_papers:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3 style="color: #e2e8f0;">Your reading list is empty</h3>
            <p style="color: #94a3b8;">Go to Search or 🧠 My AI tab and save some papers!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"📚 You have **{len(saved_papers)}** saved papers")
        
        for paper in saved_papers:
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    render_paper_card(paper)
                
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_{paper.arxiv_id}", use_container_width=True):
                        db.remove_from_reading_list(paper.arxiv_id)
                        st.toast(f"Removed from reading list!")
                        st.rerun()
                         

elif page == "🧠 My AI":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        🧠 My Personal AI
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Your AI learns from your labels to find papers you'll love
    </p>
    """, unsafe_allow_html=True)
    
    stats = db.get_stats()
    labeled_count = stats.get('labeled_papers', 0)
    positive_count = stats.get('positive_labels', 0)
    negative_count = stats.get('negative_labels', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Labeled Papers", str(labeled_count), "🏷️")
    with col2:
        render_metric_card("Relevant", str(positive_count), "👍")
    with col3:
        render_metric_card("Not Relevant", str(negative_count), "👎")
    with col4:
        status_icon = "✅" if ml_engine.is_trained else "⏳"
        render_metric_card("Model Status", "Trained" if ml_engine.is_trained else "Not Yet", status_icon)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Training section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 20px;">🎓 Train Your AI</h2>', unsafe_allow_html=True)
    
    can_train = labeled_count >= 5 and positive_count >= 2 and negative_count >= 2
    
    if not can_train:
        st.warning(f"""
        **Need more labels to train!**
        - ✅ Labeled: {labeled_count}/5 minimum
        - 👍 Relevant: {positive_count}/2 minimum  
        - 👎 Not Relevant: {negative_count}/2 minimum
        
        Go to **🏷️ Label Papers** to label more!
        """)
    else:
        st.success(f"✅ Ready to train! You have {labeled_count} labeled papers.")
        
        if st.button("🚀 Train My AI", use_container_width=True, type="primary"):
            with st.spinner("Training your personal AI..."):
                result = ml_engine.train(min_samples=5)
            
            if result.get('success'):
                st.balloons()
                st.success(f"""
                **🎉 Training Complete!**
                - Accuracy: {result['accuracy']:.1%}
                - Precision: {result['precision']:.1%}
                - F1 Score: {result['f1']:.1%}
                - Trained on: {result['samples']} papers
                """)
                st.rerun()
            else:
                st.error(f"Training failed: {result.get('error')}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Model info if trained
    if ml_engine.is_trained:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #e2e8f0; margin: 0 0 20px;">📈 Model Performance</h3>', unsafe_allow_html=True)
            
            prefs = db.get_preferences()
            if prefs.model_accuracy:
                st.metric("Accuracy", f"{prefs.model_accuracy:.1%}")
            if prefs.model_last_trained:
                st.metric("Last Trained", prefs.model_last_trained.strftime("%Y-%m-%d %H:%M"))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #e2e8f0; margin: 0 0 20px;">🔑 What Your AI Learned</h3>', unsafe_allow_html=True)
            
            model_state = db.get_active_model()
            if model_state:
                import json
                try:
                    top_pos = json.loads(model_state.top_positive_features or '[]')
                    top_neg = json.loads(model_state.top_negative_features or '[]')
                    
                    st.markdown("**Topics you like:**")
                    for item in top_pos[:5]:
                        st.markdown(f"- 👍 {item['word']}")
                    
                    st.markdown("**Topics you avoid:**")
                    for item in top_neg[:5]:
                        st.markdown(f"- 👎 {item['word']}")
                except:
                    pass
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <h2 style="font-size: 32px; margin: 32px 0 24px; color: #e2e8f0;">✨ AI Recommendations</h2>
        <p style="color: #94a3b8; margin-bottom: 24px;">Papers your AI thinks you'll love</p>
        """, unsafe_allow_html=True)
        
        recommendations = ml_engine.get_recommendations(limit=5)
        
        if recommendations:
            for idx, paper in enumerate(recommendations):
                pred_score = ml_engine.predict_relevance(paper)
                
                # Check if this paper is saved
                current_paper = db.get_paper_by_id(paper.arxiv_id)
                is_already_saved = current_paper.is_saved if current_paper else False
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"### {clean_text(paper.title)[:100]}")
                        st.markdown(f"*{clean_text(paper.authors)[:80]}*")
                    with col2:
                        if pred_score:
                            color = "#10b981" if pred_score >= 0.7 else "#3b82f6"
                            st.markdown(f"""
                            <div style="background: {color}; color: white; padding: 12px 16px; 
                                        border-radius: 12px; text-align: center; font-weight: 700;">
                                🤖 {pred_score:.0%}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.write(clean_text(paper.summary)[:300] + "...")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.link_button("📄 PDF", paper.pdf_url or "#", use_container_width=True)
                    with col2:
                        if st.button("👍 Relevant", key=f"ai_rel_{paper.arxiv_id}_{idx}"):
                            db.label_paper(paper.arxiv_id, 1)
                            st.toast("✅ Labeled as relevant!")
                            st.rerun()
                    with col3:
                        if st.button("👎 Not Relevant", key=f"ai_not_{paper.arxiv_id}_{idx}"):
                            db.label_paper(paper.arxiv_id, 0)
                            st.toast("❌ Labeled as not relevant!")
                            st.rerun()
                    with col4:
                        if is_already_saved:
                            st.success("✓ Saved")
                        else:
                            if st.button("💾 Save", key=f"ai_save_{paper.arxiv_id}_{idx}", use_container_width=True):
                                success = db.save_to_reading_list(paper.arxiv_id)
                                if success:
                                    st.toast("✅ Saved to reading list!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Failed to save - paper might not exist")
                    
                    st.divider()
        else:
            st.info("Label more papers to get personalized recommendations!")
        
        # Score all papers button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Re-score All Papers with My AI", use_container_width=True):
            with st.spinner("Scoring all papers..."):
                scores = ml_engine.score_all_papers()
            st.success(f"✅ Updated scores for {len(scores)} papers!")
    
    # Your interests
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 20px;">📊 Your Research Interests</h2>', unsafe_allow_html=True)
    
    interests = db.get_user_interests()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📂 Top Categories**")
        if interests['categories']:
            for cat, count in list(interests['categories'].items())[:8]:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 10px 16px; 
                            background: rgba(139, 92, 246, 0.1); border-radius: 8px; margin: 8px 0;">
                    <span style="color: #e2e8f0;">{cat}</span>
                    <span style="color: #8b5cf6; font-weight: 700;">{count}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Label some papers to see categories!")
    
    with col2:
        st.markdown("**🔑 Top Keywords**")
        if interests['keywords']:
            keywords_html = ' '.join([
                f'<span style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 6px 14px; border-radius: 20px; margin: 4px; display: inline-block; font-size: 14px;">{kw}</span>'
                for kw in interests['keywords'][:15]
            ])
            st.markdown(keywords_html, unsafe_allow_html=True)
        else:
            st.info("Save and label more papers to see your keywords!")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "⚙️ Settings":
    st.markdown("""
    <h1 style='text-align: center; font-size: 56px; margin: 60px 0 24px;'>
        ⚙️ Settings
    </h1>
    <p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 60px;'>
        Configure your Paper Discovery Engine
    </p>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Digest", "🔔 Notifications", "💾 Database", "📋 Commands"])
    
    # =========================================================================
    # TAB 1: EMAIL DIGEST
    # =========================================================================
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 24px;">📬 Email Digest Settings</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; margin-bottom: 24px;">Get new papers matching your interests delivered to your inbox</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        prefs = db.get_preferences()
        
        with st.form("email_settings"):
            st.markdown("### 📧 Your Email")
            email = st.text_input("Email Address", value=prefs.email or "", placeholder="your@email.com")
            
            st.markdown("### 📅 Digest Frequency")
            col1, col2 = st.columns(2)
            with col1:
                freq_options = ["none", "daily", "weekly"]
                current_freq = prefs.digest_frequency if prefs.digest_frequency in freq_options else "weekly"
                frequency = st.selectbox("How often?", freq_options, index=freq_options.index(current_freq))
            with col2:
                if frequency == "weekly":
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    digest_day = st.selectbox("Which day?", days, index=prefs.digest_day or 0)
                    digest_day_idx = days.index(digest_day)
                else:
                    digest_day_idx = 0
            
            st.markdown("### ⚙️ Digest Options")
            col1, col2 = st.columns(2)
            with col1:
                min_score = st.slider("Minimum relevance score", 0.0, 1.0, prefs.min_relevance_score or 0.5, 0.1, format="%.0f%%")
            with col2:
                max_papers = st.number_input("Max papers per digest", 5, 30, prefs.max_papers_per_digest or 10)
            
            st.markdown("### 🔐 SMTP Settings")
            st.info("For Gmail: Use an App Password, not your regular password. [Learn more](https://support.google.com/accounts/answer/185833)")
            
            col1, col2 = st.columns(2)
            with col1:
                smtp_host = st.text_input("SMTP Host", value=prefs.smtp_host or "smtp.gmail.com")
                smtp_user = st.text_input("SMTP Username (email)", value=prefs.smtp_user or "")
            with col2:
                smtp_port = st.number_input("SMTP Port", value=prefs.smtp_port or 587)
                smtp_password = st.text_input("SMTP Password", type="password", value="")
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("💾 Save Settings", use_container_width=True)
            with col2:
                test_btn = st.form_submit_button("📧 Send Test Email", use_container_width=True)
        
        if save_btn:
            # Clean all form inputs before saving
            email = clean_form_input(email)
            smtp_host = clean_form_input(smtp_host)
            smtp_user = clean_form_input(smtp_user)
            
            db.update_preferences(
                email=email,
                digest_enabled=frequency != "none",
                digest_frequency=frequency,
                digest_day=digest_day_idx,
                min_relevance_score=min_score,
                max_papers_per_digest=max_papers,
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                smtp_user=smtp_user if smtp_user else prefs.smtp_user,
                smtp_password=smtp_password if smtp_password else prefs.smtp_password
            )
            
            if smtp_user and smtp_password:
                email_service.configure(smtp_host, smtp_port, smtp_user, smtp_password)
            
            st.success("✅ Settings saved!")

        
        if test_btn:
            # Clean email input
            email = clean_form_input(email)
            
            if not email:
                st.error("Please enter your email address first!")
            elif not (smtp_user or prefs.smtp_user) or not (smtp_password or prefs.smtp_password):
                st.error("Please configure SMTP settings first!")
            else:
                if smtp_user and smtp_password:
                    email_service.configure(smtp_host, smtp_port, smtp_user, smtp_password)
                
                with st.spinner("Sending test email..."):
                    success, message = email_service.send_test_email(email)
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")
        
        # Manual digest send
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📤 Send Digest Now")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            days_back = st.selectbox("Papers from last", [1, 3, 7, 14, 30], index=2)
        with col2:
            if st.button("📬 Send Digest Now", use_container_width=True):
                prefs = db.get_preferences()
                if not prefs.email:
                    st.error("Please set your email address first!")
                else:
                    papers = db.get_papers_for_digest(since_days=days_back)
                    if not papers:
                        st.warning("No new relevant papers found!")
                    else:
                        with st.spinner(f"Sending digest with {len(papers)} papers..."):
                            success, message = email_service.send_digest(prefs.email, papers, "manual")
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
        
        # Digest history
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📜 Digest History")
        
        history = db.get_digest_history(limit=10)
        if history:
            for h in history:
                status_icon = "✅" if h.status == "sent" else "❌"
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 12px 16px;
                            background: rgba(139, 92, 246, 0.1); border-radius: 8px; margin: 8px 0;">
                    <span style="color: #e2e8f0;">{status_icon} {h.digest_type.title()} - {h.paper_count} papers</span>
                    <span style="color: #94a3b8;">{h.sent_at.strftime('%Y-%m-%d %H:%M')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No digests sent yet")
    
    # =========================================================================
    # TAB 2: NOTIFICATIONS
    # =========================================================================
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 24px;">🔔 Notification Settings</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        prefs = db.get_preferences()
        
        notify_high = st.toggle("🔥 Notify for high-relevance papers (90%+)", value=prefs.notify_high_relevance)
        auto_train = st.toggle("🤖 Auto-train AI when new labels added", value=prefs.auto_train)
        
        if st.button("💾 Save Notification Settings"):
            db.update_preferences(notify_high_relevance=notify_high, auto_train=auto_train)
            st.success("✅ Saved!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📂 Track Specific Topics")
        st.info("Select categories to focus your digest on specific areas")
        
        all_categories = db.get_categories()
        tracked = prefs.get_tracked_categories()
        
        selected_cats = st.multiselect(
            "Categories to track",
            all_categories,
            default=[c for c in tracked if c in all_categories]
        )
        
        if st.button("💾 Save Tracked Categories"):
            prefs.set_tracked_categories(selected_cats)
            db.session.commit()
            st.success(f"✅ Now tracking {len(selected_cats)} categories!")
    
    # =========================================================================
    # TAB 3: DATABASE
    # =========================================================================
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 24px;">💾 Database Status</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        stats = db.get_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Papers", f"{stats.get('total_papers', 0):,}", "📄")
        with col2:
            render_metric_card("Labeled", f"{stats.get('labeled_papers', 0):,}", "🏷️")
        with col3:
            render_metric_card("Saved", f"{stats.get('saved_papers', 0):,}", "💾")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**📁 Database Path:** `{DB_PATH}`")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧠 AI Model Status")
        
        model_state = db.get_active_model()
        if model_state:
            st.success(f"""
            ✅ **Model Active**
            - Trained: {model_state.trained_at.strftime('%Y-%m-%d %H:%M') if model_state.trained_at else 'Unknown'}
            - Samples: {model_state.training_samples}
            - Accuracy: {f"{model_state.accuracy:.1%}" if model_state.accuracy else 'N/A'}
            """)
        else:
            st.warning("No trained model yet. Go to 🧠 My AI to train!")
    
    # =========================================================================
    # TAB 4: COMMANDS
    # =========================================================================
    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 24px;">📋 Command Reference</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        commands = [
            ("🔄 Fetch New Papers", "python src/daily_run.py", "Fetches latest papers from arXiv"),
            ("📧 Run Scheduler", "python src/scheduler.py", "Runs background digest scheduler"),
        ]
        
        for title, cmd, desc in commands:
            st.markdown(f"""
            <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2);
                        border-radius: 16px; padding: 24px; margin: 16px 0;">
                <div style="font-weight: 700; color: #e2e8f0; font-size: 18px; margin-bottom: 12px;">{title}</div>
                <code style="display: block; background: #0f172a; color: #22d3ee; padding: 14px 18px; 
                            border-radius: 10px; font-size: 14px; margin: 12px 0;">{cmd}</code>
                <div style="font-size: 14px; color: #94a3b8; margin-top: 8px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.markdown(f"""
<div style="text-align: center; padding: 32px 0; color: #64748b; font-size: 14px;">
    Paper Discovery Engine  • Built with ❤️ using Python & Streamlit • {datetime.now().year}
</div>
""", unsafe_allow_html=True)