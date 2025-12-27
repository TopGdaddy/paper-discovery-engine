"""
dashboard.py - Research Intelligence Platform
Professional paper discovery and analysis system.
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

# =============================================================================
# THEME STATE
# =============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default theme

st.set_page_config(
    page_title="Research Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# =============================================================================
# PROFESSIONAL CSS DESIGN SYSTEM
# =============================================================================

def get_theme_css(theme):
    """Return CSS based on selected theme"""
    
    if theme == 'dark':
        # === YOUR EXACT DARK THEME (unchanged) ===
        return """
<style>
    /* ================================================================
       PROFESSIONAL RESEARCH PLATFORM - DESIGN SYSTEM
       Version: 2.0
       Philosophy: Scholarly, Data-Dense, Calm, Professional
       ================================================================ */

    /* === FONT IMPORTS === */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* === CSS CUSTOM PROPERTIES (Design Tokens) === */
    :root {
        /* Primary Colors */
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-200: #bfdbfe;
        --primary-300: #93c5fd;
        --primary-400: #60a5fa;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-800: #1e40af;
        --primary-900: #1e3a8a;

        /* Neutral Colors (Slate) */
        --slate-50: #f8fafc;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-300: #cbd5e1;
        --slate-400: #94a3b8;
        --slate-500: #64748b;
        --slate-600: #475569;
        --slate-700: #334155;
        --slate-800: #1e293b;
        --slate-900: #0f172a;
        --slate-950: #020617;

        /* Semantic Colors */
        --success-400: #4ade80;
        --success-500: #22c55e;
        --success-600: #16a34a;
        --warning-400: #fbbf24;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        --error-400: #f87171;
        --error-500: #ef4444;
        --error-600: #dc2626;

        /* Accent (for highlights) */
        --accent-400: #a78bfa;
        --accent-500: #8b5cf6;
        --accent-600: #7c3aed;

        /* Typography */
        --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'IBM Plex Mono', 'SF Mono', 'Consolas', monospace;
        
        /* Font Sizes */
        --text-xs: 0.75rem;
        --text-sm: 0.875rem;
        --text-base: 1rem;
        --text-lg: 1.125rem;
        --text-xl: 1.25rem;
        --text-2xl: 1.5rem;
        --text-3xl: 2rem;

        /* Spacing */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-10: 2.5rem;
        --space-12: 3rem;
        --space-16: 4rem;

        /* Border Radius */
        --radius-sm: 4px;
        --radius-md: 6px;
        --radius-lg: 8px;
        --radius-xl: 12px;

        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);

        /* Transitions */
        --transition-fast: 150ms ease;
        --transition-base: 200ms ease;
        --transition-slow: 300ms ease;
    }

    /* === BASE STYLES === */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        font-family: var(--font-sans) !important;
        background: linear-gradient(180deg, var(--slate-900) 0%, var(--slate-950) 100%) !important;
        color: var(--slate-300) !important;
        line-height: 1.6 !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }

    /* === MAIN CONTAINER === */
    .block-container {
        padding: var(--space-8) var(--space-6) var(--space-16) !important;
        max-width: 1400px !important;
    }

    /* === HIDE STREAMLIT BRANDING (keep sidebar toggle) === */
    #MainMenu, footer {
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: auto !important;
    }

    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        background: var(--slate-800) !important;
        border: 1px solid var(--slate-600) !important;
        border-radius: var(--radius-md) !important;
        padding: 8px !important;
        margin: 8px !important;
        transition: all var(--transition-fast) !important;
    }

    [data-testid="collapsedControl"]:hover {
        background: var(--slate-700) !important;
        border-color: var(--primary-500) !important;
    }

    [data-testid="collapsedControl"] svg {
        color: var(--slate-300) !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: var(--slate-800) !important;
        border-right: 1px solid var(--slate-700) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: var(--space-6) var(--space-4) !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: var(--space-1) !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: var(--slate-300) !important;
        padding: var(--space-3) var(--space-4) !important;
        border-radius: var(--radius-md) !important;
        border-left: 3px solid transparent !important;
        transition: all var(--transition-fast) !important;
        background: transparent !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--slate-700) !important;
        color: var(--slate-100) !important;
        border-left-color: var(--primary-500) !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: rgba(59, 130, 246, 0.1) !important;
        color: var(--primary-400) !important;
        border-left-color: var(--primary-500) !important;
    }

    /* === TYPOGRAPHY === */
    h1 {
        font-family: var(--font-sans) !important;
        font-size: var(--text-3xl) !important;
        font-weight: 700 !important;
        color: var(--slate-50) !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
        margin-bottom: var(--space-2) !important;
    }

    h2 {
        font-family: var(--font-sans) !important;
        font-size: var(--text-xl) !important;
        font-weight: 600 !important;
        color: var(--slate-100) !important;
        letter-spacing: -0.01em !important;
        margin-top: var(--space-8) !important;
        margin-bottom: var(--space-4) !important;
        padding-bottom: var(--space-3) !important;
        border-bottom: 1px solid var(--slate-700) !important;
    }

    h3 {
        font-family: var(--font-sans) !important;
        font-size: var(--text-lg) !important;
        font-weight: 600 !important;
        color: var(--slate-200) !important;
        margin-top: var(--space-6) !important;
        margin-bottom: var(--space-3) !important;
    }

    p, .stMarkdown, .stText {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        color: var(--slate-400) !important;
        line-height: 1.7 !important;
    }

    a {
        color: var(--primary-400) !important;
        text-decoration: none !important;
        transition: color var(--transition-fast) !important;
    }

    a:hover {
        color: var(--primary-300) !important;
        text-decoration: underline !important;
    }

    /* === PROFESSIONAL PAPER CARD === */
    .paper-card-pro {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-4) 0;
        transition: all var(--transition-base);
        position: relative;
    }

    .paper-card-pro:hover {
        border-color: var(--slate-600);
        box-shadow: var(--shadow-lg);
    }

    .paper-card-pro .paper-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: var(--space-4);
        margin-bottom: var(--space-3);
    }

    .paper-card-pro .paper-title {
        font-family: var(--font-sans);
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--slate-100);
        line-height: 1.4;
        margin: 0;
        flex: 1;
    }

    .paper-card-pro .paper-meta {
        font-family: var(--font-sans);
        font-size: var(--text-xs);
        color: var(--slate-500);
        margin-bottom: var(--space-3);
        display: flex;
        align-items: center;
        gap: var(--space-2);
        flex-wrap: wrap;
    }

    .paper-card-pro .paper-abstract {
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        color: var(--slate-400);
        line-height: 1.7;
        margin-bottom: var(--space-4);
    }

    .paper-card-pro .paper-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: var(--space-4);
        border-top: 1px solid var(--slate-700);
    }

    /* === RELEVANCE INDICATOR === */
    .relevance-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-1) var(--space-3);
        border-radius: 100px;
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }

    .relevance-high {
        background: rgba(34, 197, 94, 0.1);
        color: var(--success-400);
        border: 1px solid rgba(34, 197, 94, 0.2);
    }

    .relevance-medium {
        background: rgba(59, 130, 246, 0.1);
        color: var(--primary-400);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }

    .relevance-low {
        background: rgba(100, 116, 139, 0.1);
        color: var(--slate-400);
        border: 1px solid rgba(100, 116, 139, 0.2);
    }

    /* === CATEGORY TAG === */
    .category-tag {
        display: inline-block;
        padding: var(--space-1) var(--space-2);
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 500;
        color: var(--accent-400);
    }

    /* === METRIC CARDS === */
    .metric-card-pro {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        text-align: center;
        transition: all var(--transition-base);
    }

    .metric-card-pro:hover {
        border-color: var(--slate-600);
    }

    .metric-card-pro .metric-label {
        font-family: var(--font-sans);
        font-size: 11px;
        font-weight: 600;
        color: var(--slate-500);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: var(--space-2);
    }

    .metric-card-pro .metric-value {
        font-family: var(--font-mono);
        font-size: var(--text-2xl);
        font-weight: 600;
        color: var(--slate-50);
        line-height: 1;
    }

    /* === BUTTONS === */
    .stButton > button {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-2) var(--space-4) !important;
        height: auto !important;
        min-height: 40px !important;
        transition: all var(--transition-fast) !important;
        border: 1px solid transparent !important;
    }

    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--primary-600) !important;
        color: white !important;
        border-color: var(--primary-600) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: var(--primary-700) !important;
        border-color: var(--primary-700) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        color: var(--slate-300) !important;
        border-color: var(--slate-600) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: var(--slate-700) !important;
        border-color: var(--slate-500) !important;
        color: var(--slate-100) !important;
    }

    /* === FORM INPUTS === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        background: var(--slate-800) !important;
        border: 1px solid var(--slate-600) !important;
        border-radius: var(--radius-md) !important;
        color: var(--slate-200) !important;
        transition: all var(--transition-fast) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--space-1) !important;
        background: var(--slate-800) !important;
        padding: var(--space-1) !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--slate-700) !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: var(--slate-400) !important;
        background: transparent !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-2) var(--space-4) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-600) !important;
        color: white !important;
    }

    /* === EMPTY STATE === */
    .empty-state-pro {
        text-align: center;
        padding: var(--space-16) var(--space-8);
        background: var(--slate-800);
        border: 1px dashed var(--slate-600);
        border-radius: var(--radius-xl);
    }

    .empty-state-pro h3 {
        font-family: var(--font-sans);
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--slate-300);
        margin-bottom: var(--space-2);
    }

    .empty-state-pro p {
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        color: var(--slate-500);
    }

    /* === GLASS CARD === */
    .glass-card {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-4) 0;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--slate-900);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--slate-600);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--slate-500);
    }

    /* === METRIC COMPONENT === */
    [data-testid="stMetric"] {
        background: var(--slate-800) !important;
        border: 1px solid var(--slate-700) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-4) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: var(--slate-500) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 600 !important;
        color: var(--slate-50) !important;
    }

    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .block-container {
            padding: var(--space-4) var(--space-3) var(--space-12) !important;
        }

        h1 {
            font-size: var(--text-2xl) !important;
        }

        h2 {
            font-size: var(--text-lg) !important;
        }

        .paper-card-pro {
            padding: var(--space-4) !important;
        }

        .metric-card-pro {
            padding: var(--space-4) !important;
        }

        .metric-card-pro .metric-value {
            font-size: var(--text-xl) !important;
        }
    }
</style>
"""
    
    else:  # Light theme
        return """
<style>
    /* ================================================================
       PROFESSIONAL RESEARCH PLATFORM - LIGHT THEME
       Version: 2.0
       ================================================================ */

    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-200: #bfdbfe;
        --primary-300: #93c5fd;
        --primary-400: #60a5fa;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-800: #1e40af;
        --primary-900: #1e3a8a;

        --slate-50: #f8fafc;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-300: #cbd5e1;
        --slate-400: #94a3b8;
        --slate-500: #64748b;
        --slate-600: #475569;
        --slate-700: #334155;
        --slate-800: #1e293b;
        --slate-900: #0f172a;
        --slate-950: #020617;

        --success-400: #4ade80;
        --success-500: #22c55e;
        --success-600: #16a34a;
        --warning-400: #fbbf24;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        --error-400: #f87171;
        --error-500: #ef4444;
        --error-600: #dc2626;

        --accent-400: #a78bfa;
        --accent-500: #8b5cf6;
        --accent-600: #7c3aed;

        --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'IBM Plex Mono', 'SF Mono', 'Consolas', monospace;
        
        --text-xs: 0.75rem;
        --text-sm: 0.875rem;
        --text-base: 1rem;
        --text-lg: 1.125rem;
        --text-xl: 1.25rem;
        --text-2xl: 1.5rem;
        --text-3xl: 2rem;

        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-10: 2.5rem;
        --space-12: 3rem;
        --space-16: 4rem;

        --radius-sm: 4px;
        --radius-md: 6px;
        --radius-lg: 8px;
        --radius-xl: 12px;

        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.05);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.03);

        --transition-fast: 150ms ease;
        --transition-base: 200ms ease;
        --transition-slow: 300ms ease;
    }

    /* === BASE STYLES === */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        font-family: var(--font-sans) !important;
        background: var(--slate-50) !important;
        color: var(--slate-700) !important;
        line-height: 1.6 !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }

    .block-container {
        padding: var(--space-8) var(--space-6) var(--space-16) !important;
        max-width: 1400px !important;
    }

    #MainMenu, footer {
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: auto !important;
    }

    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        background: white !important;
        border: 1px solid var(--slate-200) !important;
        border-radius: var(--radius-md) !important;
        padding: 8px !important;
        margin: 8px !important;
        transition: all var(--transition-fast) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    [data-testid="collapsedControl"]:hover {
        background: var(--slate-50) !important;
        border-color: var(--primary-500) !important;
    }

    [data-testid="collapsedControl"] svg {
        color: var(--slate-600) !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid var(--slate-200) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: var(--space-6) var(--space-4) !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: var(--space-1) !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: var(--slate-600) !important;
        padding: var(--space-3) var(--space-4) !important;
        border-radius: var(--radius-md) !important;
        border-left: 3px solid transparent !important;
        transition: all var(--transition-fast) !important;
        background: transparent !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--slate-100) !important;
        color: var(--slate-900) !important;
        border-left-color: var(--primary-500) !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: var(--primary-50) !important;
        color: var(--primary-700) !important;
        border-left-color: var(--primary-500) !important;
    }

    /* === TYPOGRAPHY === */
    h1 {
        font-family: var(--font-sans) !important;
        font-size: var(--text-3xl) !important;
        font-weight: 700 !important;
        color: var(--slate-900) !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
        margin-bottom: var(--space-2) !important;
    }

    h2 {
        font-family: var(--font-sans) !important;
        font-size: var(--text-xl) !important;
        font-weight: 600 !important;
        color: var(--slate-800) !important;
        letter-spacing: -0.01em !important;
        margin-top: var(--space-8) !important;
        margin-bottom: var(--space-4) !important;
        padding-bottom: var(--space-3) !important;
        border-bottom: 1px solid var(--slate-200) !important;
    }

    h3 {
        font-family: var(--font-sans) !important;
        font-size: var(--text-lg) !important;
        font-weight: 600 !important;
        color: var(--slate-800) !important;
        margin-top: var(--space-6) !important;
        margin-bottom: var(--space-3) !important;
    }

    p, .stMarkdown, .stText {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        color: var(--slate-600) !important;
        line-height: 1.7 !important;
    }

    a {
        color: var(--primary-600) !important;
        text-decoration: none !important;
        transition: color var(--transition-fast) !important;
    }

    a:hover {
        color: var(--primary-700) !important;
        text-decoration: underline !important;
    }

    /* === PROFESSIONAL PAPER CARD === */
    .paper-card-pro {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-4) 0;
        transition: all var(--transition-base);
        position: relative;
        box-shadow: var(--shadow-sm);
    }

    .paper-card-pro:hover {
        border-color: var(--primary-300);
        box-shadow: var(--shadow-md);
    }

    .paper-card-pro .paper-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: var(--space-4);
        margin-bottom: var(--space-3);
    }

    .paper-card-pro .paper-title {
        font-family: var(--font-sans);
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--slate-900);
        line-height: 1.4;
        margin: 0;
        flex: 1;
    }

    .paper-card-pro .paper-meta {
        font-family: var(--font-sans);
        font-size: var(--text-xs);
        color: var(--slate-500);
        margin-bottom: var(--space-3);
        display: flex;
        align-items: center;
        gap: var(--space-2);
        flex-wrap: wrap;
    }

    .paper-card-pro .paper-abstract {
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        color: var(--slate-600);
        line-height: 1.7;
        margin-bottom: var(--space-4);
    }

    .paper-card-pro .paper-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: var(--space-4);
        border-top: 1px solid var(--slate-200);
    }

    /* === RELEVANCE INDICATOR === */
    .relevance-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-1) var(--space-3);
        border-radius: 100px;
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }

    .relevance-high {
        background: rgba(22, 163, 74, 0.1);
        color: var(--success-600);
        border: 1px solid rgba(22, 163, 74, 0.2);
    }

    .relevance-medium {
        background: rgba(37, 99, 235, 0.1);
        color: var(--primary-700);
        border: 1px solid rgba(37, 99, 235, 0.2);
    }

    .relevance-low {
        background: rgba(100, 116, 139, 0.1);
        color: var(--slate-600);
        border: 1px solid rgba(100, 116, 139, 0.2);
    }

    /* === CATEGORY TAG === */
    .category-tag {
        display: inline-block;
        padding: var(--space-1) var(--space-2);
        background: rgba(124, 58, 237, 0.1);
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 500;
        color: var(--accent-600);
    }

    /* === METRIC CARDS === */
    .metric-card-pro {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        text-align: center;
        transition: all var(--transition-base);
        box-shadow: var(--shadow-sm);
    }

    .metric-card-pro:hover {
        border-color: var(--slate-300);
        box-shadow: var(--shadow-md);
    }

    .metric-card-pro .metric-label {
        font-family: var(--font-sans);
        font-size: 11px;
        font-weight: 600;
        color: var(--slate-500);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: var(--space-2);
    }

    .metric-card-pro .metric-value {
        font-family: var(--font-mono);
        font-size: var(--text-2xl);
        font-weight: 600;
        color: var(--slate-900);
        line-height: 1;
    }

    /* === BUTTONS === */
    .stButton > button {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-2) var(--space-4) !important;
        height: auto !important;
        min-height: 40px !important;
        transition: all var(--transition-fast) !important;
        border: 1px solid transparent !important;
    }

    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--primary-600) !important;
        color: white !important;
        border-color: var(--primary-600) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: var(--primary-700) !important;
        border-color: var(--primary-700) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {
        background: white !important;
        color: var(--slate-700) !important;
        border-color: var(--slate-300) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: var(--slate-50) !important;
        border-color: var(--slate-400) !important;
        color: var(--slate-900) !important;
    }

    /* === FORM INPUTS === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        background: white !important;
        border: 1px solid var(--slate-300) !important;
        border-radius: var(--radius-md) !important;
        color: var(--slate-900) !important;
        transition: all var(--transition-fast) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--space-1) !important;
        background: var(--slate-100) !important;
        padding: var(--space-1) !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--slate-200) !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: var(--slate-600) !important;
        background: transparent !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-2) var(--space-4) !important;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--primary-700) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* === EMPTY STATE === */
    .empty-state-pro {
        text-align: center;
        padding: var(--space-16) var(--space-8);
        background: white;
        border: 1px dashed var(--slate-300);
        border-radius: var(--radius-xl);
    }

    .empty-state-pro h3 {
        font-family: var(--font-sans);
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--slate-700);
        margin-bottom: var(--space-2);
    }

    .empty-state-pro p {
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        color: var(--slate-500);
    }

    /* === GLASS CARD === */
    .glass-card {
        background: white;
        border: 1px solid var(--slate-200);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-4) 0;
        box-shadow: var(--shadow-sm);
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--slate-100);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--slate-300);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--slate-400);
    }

    /* === METRIC COMPONENT === */
    [data-testid="stMetric"] {
        background: white !important;
        border: 1px solid var(--slate-200) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-4) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: var(--slate-500) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 600 !important;
        color: var(--slate-900) !important;
    }

    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .block-container {
            padding: var(--space-4) var(--space-3) var(--space-12) !important;
        }

        h1 {
            font-size: var(--text-2xl) !important;
        }

        h2 {
            font-size: var(--text-lg) !important;
        }

        .paper-card-pro {
            padding: var(--space-4) !important;
        }

        .metric-card-pro {
            padding: var(--space-4) !important;
        }

        .metric-card-pro .metric-value {
            font-size: var(--text-xl) !important;
        }
    }
</style>
"""

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
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
    
    text = text.replace('\xa0', ' ')
    text = text.replace('\u200b', '')
    text = text.replace('\r', '')
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    
    return text.strip()

def clean_form_input(text):
    """Clean form input to remove problematic characters"""
    if not text:
        return text
    text = str(text).strip()
    text = text.replace('\xa0', ' ')
    text = text.replace('\u200b', '')
    text = text.replace('\r', '')
    text = ' '.join(text.split())
    return text

def truncate(text, length=100):
    if not text:
        return ""
    text = clean_text(text)
    return text if len(text) <= length else text[:length].rsplit(' ', 1)[0] + "..."

def get_score_style(score):
    """Returns color and badge class for score - NO EMOJIS"""
    s = score or 0
    if s >= 0.75:
        return "#10b981", "relevance-high"
    if s >= 0.60:
        return "#3b82f6", "relevance-medium"
    if s >= 0.45:
        return "#8b5cf6", "relevance-medium"
    return "#64748b", "relevance-low"

# =============================================================================
# COMPONENTS
# =============================================================================

def render_paper_card(paper: PaperRecord, show_summary=True):
    """Renders professional paper card using Streamlit components"""
    score = paper.relevance_score or 0
    color, badge_class = get_score_style(score)
    
    title = clean_text(paper.title or "Untitled Paper")
    authors = clean_text(paper.authors or "Unknown Authors")
    summary = clean_text(paper.summary or "") if show_summary else ""
    category = clean_text(paper.primary_category or "Unknown")
    
    title = title[:120] + "..." if len(title) > 120 else title
    authors = authors[:100] + "..." if len(authors) > 100 else authors
    summary = summary[:340] + "..." if len(summary) > 340 else summary
    
    pdf_url = paper.pdf_url or "#"
    abs_url = paper.abs_url or "#"
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'''
            <span class="relevance-badge {badge_class}">{score:.0%} Relevance</span>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="category-tag">{category}</span>', unsafe_allow_html=True)
        
        st.markdown(f"### [{title}]({abs_url})")
        st.markdown(f"**{authors}**")
        
        if summary:
            st.write(summary)
        
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("View PDF", pdf_url, use_container_width=True)
        with col2:
            st.link_button("arXiv Abstract", abs_url, use_container_width=True)
        
        st.divider()

def render_metric_card(label, value):
    """Render professional metric card - NO ICONS"""
    st.markdown(f"""
    <div class="metric-card-pro">
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
            color='rgba(59, 130, 246, 0.7)',
            line=dict(color='rgba(59, 130, 246, 1)', width=2)
        ),
        hovertemplate='Score: %{x:.0f}%<br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Relevance Score Distribution', font=dict(size=18, color='#e2e8f0')),
        xaxis=dict(
            title=dict(text='Relevance Score (%)', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)',
            range=[0, 100]
        ),
        yaxis=dict(
            title=dict(text='Paper Count', font=dict(size=14, color='#94a3b8')),
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
            colorscale='Blues',
            line=dict(color='rgba(59, 130, 246, 1)', width=2)
        ),
        hovertemplate='%{y}<br>Papers: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Papers by Category', font=dict(size=18, color='#e2e8f0')),
        xaxis=dict(
            title=dict(text='Paper Count', font=dict(size=14, color='#94a3b8')),
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
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#3b82f6'),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.15)',
        hovertemplate='%{x}<br>Papers: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Publication Timeline', font=dict(size=18, color='#e2e8f0')),
        xaxis=dict(
            title=dict(text='Date', font=dict(size=14, color='#94a3b8')),
            tickfont=dict(size=11, color='#94a3b8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        yaxis=dict(
            title=dict(text='Paper Count', font=dict(size=14, color='#94a3b8')),
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
    
    existing = db.session.query(PaperRecord).filter_by(arxiv_id=arxiv_id).first()
    if existing:
        return False, "Already in library"
    
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
        relevance_score=0.95
    )
    
    db.session.add(new_paper)
    db.session.commit()
    return True, "Added to library"

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
    """Fetch trending posts from Reddit, with fallback data"""
    if requests is None: 
        return get_reddit_fallback()
    
    trending = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for sub in ['MachineLearning', 'artificial']:
            try:
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                resp = requests.get(url, headers=headers, timeout=8)
                
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
            except requests.exceptions.RequestException as e:
                continue
        
        if trending:
            trending.sort(key=lambda x: x['score'], reverse=True)
            return trending[:5]
        else: 
            return get_reddit_fallback()
            
    except Exception as e:
        return get_reddit_fallback()

def get_reddit_fallback():
    """Return static fallback trending data"""
    return [
        {
            'title': 'Latest developments in AI & Machine Learning',
            'score': 5000,
            'url': 'https://reddit.com/r/MachineLearning',
            'source': 'r/MachineLearning'
        },
        {
            'title': 'Artificial Intelligence research discussions',
            'score': 3500,
            'url': 'https://reddit.com/r/artificial',
            'source': 'r/artificial'
        },
    ]

# =============================================================================
# SIDEBAR - PROFESSIONAL VERSION
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px 30px;">
        <h1 style="font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px; color: #f1f5f9;">
            Research Intelligence
        </h1>
        <p style="color: #64748b; font-size: 14px; margin-top: 8px; font-weight: 500;">
            Paper Discovery Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # PROFESSIONAL NAVIGATION - No emojis
    page = st.radio(
        "Navigate",
        ["Dashboard", "Literature Repository", "Search", "Library", "Training Data", "Model", "Analytics", "Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Quick Stats - Professional labels
    st.markdown("**Overview**")
    col1, col2 = st.columns(2)
    with col1:
        try:
            paper_count = db.count_papers()
            st.metric("Papers", f"{paper_count:,}")
        except:
            st.metric("Papers", "0")
    with col2:
        try:
            labeled_count = db.count_labeled()
            st.metric("Labeled", labeled_count)
        except:
            st.metric("Labeled", "0")
    
    st.divider()
    
    # Community Discussions - Professional header
    st.markdown("**Community Discussions**")

    try:
        trending = get_reddit_trending()
        
        if trending and len(trending) > 0:
            for item in trending[:4]: 
                st.markdown(f"""
                <a href="{item['url']}" target="_blank" style="
                    display: block;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    border-radius: 8px;
                    padding: 12px 14px;
                    margin: 10px 0;
                    color: #e2e8f0;
                    text-decoration: none;
                    font-size: 13px;
                    line-height: 1.5;
                    transition: all 0.2s;
                ">
                    {item['title']}<br>
                    <span style="color: #64748b; font-size: 12px;">{item['source']} · {item['score']:,} upvotes</span>
                </a>
                """, unsafe_allow_html=True)
        else:
            st.info("Community feed unavailable")
                
    except Exception as e:
        st.info("Visit r/MachineLearning for discussions")


# =============================================================================
# PAGES - PROFESSIONAL VERSIONS
# =============================================================================

if page == "Dashboard":
    st.markdown("""
    <h1 style='text-align: center; font-size: 48px; margin: 60px 0 16px; letter-spacing: -1px;'>
        Research Intelligence Dashboard
    </h1>
    <p style='text-align: center; font-size: 18px; color: #64748b; margin-bottom: 60px; font-weight: 400;'>
        Personalized recommendations based on your research interests
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
        render_metric_card("Total Papers", str(len(all_papers)))
    with col2:
        render_metric_card("High Relevance", str(high_rel))
    with col3:
        render_metric_card("Labeled", str(stats.get('labeled_papers', 0)))
    with col4:
        render_metric_card("Avg. Score", f"{avg_score:.0%}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_main, col_side = st.columns([3, 2])
    
    with col_main:
        st.markdown('<h2 style="font-size: 24px; margin: 0 0 24px; color: #f1f5f9;">High-Relevance Publications</h2>', unsafe_allow_html=True)
        if all_papers:
            top_papers = sorted(all_papers, key=lambda p: p.relevance_score or 0, reverse=True)[:5]
            for paper in top_papers:
                render_paper_card(paper, show_summary=True)
        else:
            st.markdown("""
            <div class="empty-state-pro">
                <h3>No papers in repository</h3>
                <p>Run the data pipeline to fetch papers from arXiv.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_side:
        if all_papers:
            fig = create_score_chart(all_papers)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<h3 style="font-size: 18px; margin: 32px 0 16px; color: #e2e8f0;">Category Distribution</h3>', unsafe_allow_html=True)
        
        if all_papers:
            cats = {}
            for p in all_papers:
                cat = p.primary_category or "Unknown"
                cats[cat] = cats.get(cat, 0) + 1
            
            for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:6]:
                pct = count / len(all_papers) * 100
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 12px 16px; 
                background: rgba(59, 130, 246, 0.08); border-radius: 8px; margin: 8px 0;
                border: 1px solid rgba(59, 130, 246, 0.15);">
                    <span style="color: #e2e8f0; font-weight: 500;">{cat}</span>
                    <span style="color: #64748b; font-weight: 600;">{count} ({pct:.0f}%)</span>
                </div>
                """, unsafe_allow_html=True)

elif page == "Literature Repository":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Literature Repository
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Browse and filter your paper collection
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        min_score = st.slider("Minimum Relevance", 0, 100, 0, 5, format="%d%%")
    with col2:
        try:
            categories = ["All Categories"] + db.get_categories()
        except:
            categories = ["All Categories"]
        selected_cat = st.selectbox("Category", categories)
    with col3:
        sort_opts = {
            "Relevance (High to Low)": "score_desc",
            "Relevance (Low to High)": "score_asc",
            "Date (Newest)": "date_desc",
            "Date (Oldest)": "date_asc"
        }
        sort_by = st.selectbox("Sort By", list(sort_opts.keys()))
    with col4:
        per_page = st.selectbox("Per Page", [25, 50, 100])
    
    st.divider()
    
    try:
        all_papers = db.get_all_papers(limit=2000)
    except:
        all_papers = []
    
    filtered = [p for p in all_papers if (p.relevance_score or 0) * 100 >= min_score]
    if selected_cat != "All Categories":
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
        st.markdown(f"**{total:,} papers found**")
    with col_page:
        current_page = st.number_input("Page", 1, total_pages, 1, label_visibility="collapsed")
    
    start = (current_page - 1) * per_page
    papers_to_show = filtered[start:start + per_page]
    
    for paper in papers_to_show:
        render_paper_card(paper)

elif page == "Search":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Search Publications
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Search across multiple scientific databases worldwide
    </p>
    """, unsafe_allow_html=True)

    # =========================================================================
    # SESSION STATE
    # =========================================================================
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'saved_papers' not in st.session_state:
        st.session_state.saved_papers = set()
    if 'just_saved' not in st.session_state:
        st.session_state.just_saved = None
    if 'search_source' not in st.session_state:
        st.session_state.search_source = "arXiv"

    if st.session_state.just_saved:
        st.balloons()
        st.toast(f"Added: {st.session_state.just_saved}")
        st.session_state.just_saved = None

    # =========================================================================
    # SEARCH FUNCTIONS
    # =========================================================================
    
    def search_arxiv(query, category="", max_results=20):
        """Search arXiv API"""
        import urllib.parse
        import time
        
        time.sleep(1)  # Rate limiting
        
        cat_query = f"+cat:{category}" if category else ""
        encoded = urllib.parse.quote(query)
        url = f"https://export.arxiv.org/api/query?search_query=all:{encoded}{cat_query}&max_results={max_results}&sortBy=submittedDate"
        
        headers = {'User-Agent': 'ResearchPlatform/2.0'}
        
        try:
            r = requests.get(url, headers=headers, timeout=20)
            feed = feedparser.parse(r.content)
            
            results = []
            for entry in feed.entries:
                arxiv_id = entry.link.split("/")[-1]
                
                published_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                results.append({
                    'source': 'arXiv',
                    'paper_id': arxiv_id,
                    'arxiv_id': arxiv_id,
                    'title': entry.title.replace('\n', ' ').strip(),
                    'authors': ', '.join([a.name for a in entry.authors]) if hasattr(entry, 'authors') else "Unknown",
                    'summary': entry.summary.replace('\n', ' ').strip(),
                    'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                    'abs_url': entry.link,
                    'category': entry.tags[0].term if entry.tags else "unknown",
                    'published': published_date,
                    'venue': 'arXiv Preprint'
                })
            
            return results
        except Exception as e:
            print(f"arXiv error: {e}")
            return []
    
    def search_semantic_scholar(query, max_results=20, fields_of_study=None):
        """Search Semantic Scholar API - covers ALL sciences"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        params = {
            "query": query,
            "limit": max_results,
            "fields": "paperId,title,abstract,authors,year,venue,url,openAccessPdf,fieldsOfStudy,citationCount"
        }
        
        if fields_of_study:
            params["fieldsOfStudy"] = fields_of_study
        
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get("data", [])
                
                results = []
                for paper in papers:
                    # Get PDF URL if available
                    pdf_url = None
                    if paper.get('openAccessPdf'):
                        pdf_url = paper['openAccessPdf'].get('url')
                    
                    # Get authors
                    authors = "Unknown"
                    if paper.get('authors'):
                        author_names = [a.get('name', '') for a in paper['authors'][:5]]
                        authors = ', '.join(author_names)
                        if len(paper['authors']) > 5:
                            authors += f" (+{len(paper['authors']) - 5} more)"
                    
                    # Get fields of study
                    fields = paper.get('fieldsOfStudy') or []
                    category = fields[0] if fields else "Unknown"
                    
                    results.append({
                        'source': 'Semantic Scholar',
                        'paper_id': paper.get('paperId', ''),
                        'arxiv_id': f"s2-{paper.get('paperId', '')[:12]}",  # Create pseudo-ID
                        'title': paper.get('title', 'Untitled'),
                        'authors': authors,
                        'summary': paper.get('abstract') or 'No abstract available.',
                        'pdf_url': pdf_url or paper.get('url', '#'),
                        'abs_url': f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                        'category': category,
                        'published': datetime(paper.get('year', 2024), 1, 1) if paper.get('year') else datetime.now(),
                        'venue': paper.get('venue') or 'Unknown Venue',
                        'citations': paper.get('citationCount', 0)
                    })
                
                return results
            else:
                print(f"Semantic Scholar API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Semantic Scholar error: {e}")
            return []
    
    def search_pubmed(query, max_results=20):
        """Search PubMed API - for biomedical literature"""
        # Step 1: Search for IDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        
        try:
            search_response = requests.get(search_url, params=search_params, timeout=15)
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # Step 2: Fetch details
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json"
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
            fetch_data = fetch_response.json()
            
            results = []
            for pmid in id_list:
                paper = fetch_data.get("result", {}).get(pmid, {})
                
                if not paper or paper == "uids":
                    continue
                
                # Get authors
                authors = "Unknown"
                author_list = paper.get("authors", [])
                if author_list:
                    author_names = [a.get("name", "") for a in author_list[:5]]
                    authors = ", ".join(author_names)
                    if len(author_list) > 5:
                        authors += f" (+{len(author_list) - 5} more)"
                
                # Parse date
                pub_date = datetime.now()
                try:
                    pub_date_str = paper.get("pubdate", "")
                    if pub_date_str:
                        year = int(pub_date_str.split()[0])
                        pub_date = datetime(year, 1, 1)
                except:
                    pass
                
                results.append({
                    'source': 'PubMed',
                    'paper_id': pmid,
                    'arxiv_id': f"pm-{pmid}",  # Create pseudo-ID
                    'title': paper.get("title", "Untitled"),
                    'authors': authors,
                    'summary': paper.get("title", ""),  # PubMed summary needs separate fetch
                    'pdf_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'abs_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'category': paper.get("fulljournalname", "Biomedical"),
                    'published': pub_date,
                    'venue': paper.get("source", "Unknown Journal")
                })
            
            return results
            
        except Exception as e:
            print(f"PubMed error: {e}")
            return []

    # =========================================================================
    # CATEGORY DEFINITIONS
    # =========================================================================
    
    # arXiv categories (two-step)
    arxiv_domains = {
        "All arXiv": "",
        "Computer Science": "cs",
        "Physics": "physics",
        "Mathematics": "math",
        "Statistics": "stat",
        "Quantitative Biology": "q-bio",
        "Quantitative Finance": "q-fin",
        "Electrical Engineering": "eess",
        "Economics": "econ",
    }
    
    arxiv_subcategories = {
        "cs": {
            "All Computer Science": "cs",
            "Artificial Intelligence": "cs.AI",
            "Machine Learning": "cs.LG",
            "Computer Vision": "cs.CV",
            "NLP / Computation and Language": "cs.CL",
            "Robotics": "cs.RO",
            "Neural and Evolutionary Computing": "cs.NE",
            "Information Retrieval": "cs.IR",
            "Cryptography and Security": "cs.CR",
            "Databases": "cs.DB",
            "Software Engineering": "cs.SE",
            "Human-Computer Interaction": "cs.HC",
            "Networking": "cs.NI",
            "Distributed Computing": "cs.DC",
            "Data Structures and Algorithms": "cs.DS",
            "Programming Languages": "cs.PL",
        },
        "physics": {
            "All Physics": "physics",
            "Quantum Physics": "quant-ph",
            "Astrophysics": "astro-ph",
            "Condensed Matter": "cond-mat",
            "High Energy Physics (Theory)": "hep-th",
            "High Energy Physics (Experiment)": "hep-ex",
            "General Relativity": "gr-qc",
            "Mathematical Physics": "math-ph",
            "Optics": "physics.optics",
            "Computational Physics": "physics.comp-ph",
            "Applied Physics": "physics.app-ph",
            "Fluid Dynamics": "physics.flu-dyn",
        },
        "math": {
            "All Mathematics": "math",
            "Probability": "math.PR",
            "Statistics Theory": "math.ST",
            "Optimization and Control": "math.OC",
            "Numerical Analysis": "math.NA",
            "Combinatorics": "math.CO",
            "Number Theory": "math.NT",
            "Algebraic Geometry": "math.AG",
            "Differential Geometry": "math.DG",
            "Logic": "math.LO",
        },
        "stat": {
            "All Statistics": "stat",
            "Machine Learning": "stat.ML",
            "Methodology": "stat.ME",
            "Applications": "stat.AP",
            "Computation": "stat.CO",
            "Theory": "stat.TH",
        },
        "q-bio": {
            "All Quantitative Biology": "q-bio",
            "Genomics": "q-bio.GN",
            "Neurons and Cognition": "q-bio.NC",
            "Biomolecules": "q-bio.BM",
            "Populations and Evolution": "q-bio.PE",
            "Quantitative Methods": "q-bio.QM",
        },
        "q-fin": {
            "All Quantitative Finance": "q-fin",
            "Computational Finance": "q-fin.CP",
            "Portfolio Management": "q-fin.PM",
            "Risk Management": "q-fin.RM",
            "Mathematical Finance": "q-fin.MF",
            "Trading and Microstructure": "q-fin.TR",
        },
        "eess": {
            "All Electrical Engineering": "eess",
            "Signal Processing": "eess.SP",
            "Image and Video Processing": "eess.IV",
            "Audio and Speech Processing": "eess.AS",
            "Systems and Control": "eess.SY",
        },
        "econ": {
            "All Economics": "econ",
            "Econometrics": "econ.EM",
            "Theoretical Economics": "econ.TH",
            "General Economics": "econ.GN",
        },
    }
    
    # Semantic Scholar fields
    semantic_scholar_fields = {
        "All Fields": None,
        "Computer Science": "Computer Science",
        "Physics": "Physics",
        "Mathematics": "Mathematics",
        "Biology": "Biology",
        "Medicine": "Medicine",
        "Chemistry": "Chemistry",
        "Materials Science": "Materials Science",
        "Environmental Science": "Environmental Science",
        "Psychology": "Psychology",
        "Economics": "Economics",
        "Business": "Business",
        "Engineering": "Engineering",
        "Geology": "Geology",
        "Geography": "Geography",
        "Political Science": "Political Science",
        "Sociology": "Sociology",
        "History": "History",
        "Philosophy": "Philosophy",
        "Art": "Art",
        "Law": "Law",
    }

    # =========================================================================
    # SOURCE SELECTION
    # =========================================================================
    
    st.markdown("### Select Data Source")
    
    source_col1, source_col2, source_col3 = st.columns(3)
    
    with source_col1:
        arxiv_selected = st.checkbox("arXiv", value=True, help="Physics, Math, CS, Quantitative fields")
    with source_col2:
        semantic_selected = st.checkbox("Semantic Scholar", value=False, help="All sciences including Biology, Medicine, Chemistry")
    with source_col3:
        pubmed_selected = st.checkbox("PubMed", value=False, help="Biomedical and life sciences")
    
    if not (arxiv_selected or semantic_selected or pubmed_selected):
        st.warning("Please select at least one data source")
        arxiv_selected = True
    
    st.markdown("---")

    # =========================================================================
    # SEARCH FORM
    # =========================================================================
    
    with st.form(key="search_form"):
        query = st.text_input(
            "Search Query", 
            placeholder="transformer, CRISPR, cancer treatment, quantum computing, climate change...", 
            label_visibility="collapsed"
        )
        
        # Dynamic category selection based on source
        if arxiv_selected and not (semantic_selected or pubmed_selected):
            # arXiv only - show two-step category
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                selected_domain = st.selectbox("Domain", list(arxiv_domains.keys()), index=0)
            
            with col2:
                if selected_domain == "All arXiv":
                    subcategory_options = {"All Fields": ""}
                else:
                    domain_code = arxiv_domains[selected_domain]
                    subcategory_options = arxiv_subcategories.get(domain_code, {"All": domain_code})
                
                selected_subcategory = st.selectbox("Subcategory", list(subcategory_options.keys()), index=0)
                arxiv_category = subcategory_options[selected_subcategory]
            
            with col3:
                num_results = st.selectbox("Results per source", [10, 20, 30, 50], index=1)
            
            semantic_field = None
            
        elif semantic_selected and not (arxiv_selected or pubmed_selected):
            # Semantic Scholar only
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_field = st.selectbox("Field of Study", list(semantic_scholar_fields.keys()), index=0)
                semantic_field = semantic_scholar_fields[selected_field]
            
            with col2:
                num_results = st.selectbox("Results", [10, 20, 30, 50], index=1)
            
            arxiv_category = ""
            
        else:
            # Multiple sources - simplified
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_field = st.selectbox(
                    "Field (for Semantic Scholar)", 
                    list(semantic_scholar_fields.keys()), 
                    index=0,
                    help="This filter applies to Semantic Scholar results"
                )
                semantic_field = semantic_scholar_fields[selected_field]
            
            with col2:
                num_results = st.selectbox("Results per source", [10, 20, 30], index=1)
            
            arxiv_category = ""  # Search all arXiv when multi-source
        
        submit = st.form_submit_button("Search", use_container_width=True, type="primary")

    # =========================================================================
    # EXECUTE SEARCH
    # =========================================================================
    
    if submit and query.strip():
        st.session_state.search_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        sources_to_search = []
        if arxiv_selected:
            sources_to_search.append("arXiv")
        if semantic_selected:
            sources_to_search.append("Semantic Scholar")
        if pubmed_selected:
            sources_to_search.append("PubMed")
        
        total_sources = len(sources_to_search)
        current = 0
        
        all_results = []
        
        # Search arXiv
        if arxiv_selected:
            current += 1
            progress_bar.progress(current / total_sources)
            status_text.text(f"Searching arXiv... ({current}/{total_sources})")
            
            arxiv_results = search_arxiv(query, arxiv_category, num_results)
            all_results.extend(arxiv_results)
        
        # Search Semantic Scholar
        if semantic_selected:
            current += 1
            progress_bar.progress(current / total_sources)
            status_text.text(f"Searching Semantic Scholar... ({current}/{total_sources})")
            
            ss_results = search_semantic_scholar(query, num_results, semantic_field)
            all_results.extend(ss_results)
        
        # Search PubMed
        if pubmed_selected:
            current += 1
            progress_bar.progress(current / total_sources)
            status_text.text(f"Searching PubMed... ({current}/{total_sources})")
            
            pubmed_results = search_pubmed(query, num_results)
            all_results.extend(pubmed_results)
        
        progress_bar.progress(1.0)
        status_text.empty()
        progress_bar.empty()
        
        st.session_state.search_results = all_results
        
        if all_results:
            # Show summary by source
            source_counts = {}
            for r in all_results:
                src = r.get('source', 'Unknown')
                source_counts[src] = source_counts.get(src, 0) + 1
            
            summary_parts = [f"{count} from {src}" for src, count in source_counts.items()]
            st.success(f"Found {len(all_results)} papers: {', '.join(summary_parts)}")
        else:
            st.warning("No papers found. Try different keywords or sources.")

    # =========================================================================
    # DISPLAY RESULTS
    # =========================================================================
    
    if st.session_state.search_results:
        # Get saved paper IDs
        try:
            saved_arxiv_ids = {p.arxiv_id for p in db.get_all_papers() if hasattr(p, 'arxiv_id')}
        except:
            saved_arxiv_ids = set()
        
        saved_arxiv_ids = saved_arxiv_ids.union(st.session_state.saved_papers)
        
        # Source filter
        sources_in_results = list(set(r.get('source', 'Unknown') for r in st.session_state.search_results))
        if len(sources_in_results) > 1:
            filter_source = st.selectbox(
                "Filter by source",
                ["All Sources"] + sources_in_results,
                index=0
            )
        else:
            filter_source = "All Sources"
        
        # Filter results
        filtered_results = st.session_state.search_results
        if filter_source != "All Sources":
            filtered_results = [r for r in filtered_results if r.get('source') == filter_source]
        
        st.markdown(f"**Showing {len(filtered_results)} papers**")
        st.markdown("---")
        
        # Display papers
        for i, paper in enumerate(filtered_results):
            paper_id = paper.get('arxiv_id', paper.get('paper_id', f'paper_{i}'))
            title = clean_text(paper['title'])
            authors = paper['authors']
            summary = clean_text(paper.get('summary', ''))[:400]
            if len(paper.get('summary', '')) > 400:
                summary += "..."
            pdf_url = paper.get('pdf_url', '#')
            abs_url = paper.get('abs_url', '#')
            source = paper.get('source', 'Unknown')
            venue = paper.get('venue', '')
            citations = paper.get('citations', None)
            category = paper.get('category', 'Unknown')
            
            already_saved = paper_id in saved_arxiv_ids
            
            # Source badge color
            source_colors = {
                'arXiv': '#b31b1b',
                'Semantic Scholar': '#1857b6',
                'PubMed': '#326599'
            }
            source_color = source_colors.get(source, '#64748b')
            
            with st.container():
                st.markdown(f"""
                <div class="paper-card-pro" style="border-left: 3px solid {'#10b981' if already_saved else source_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: {source_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                            {source}
                        </span>
                        <span style="color: #64748b; font-size: 12px;">
                            {category} {f'• {citations:,} citations' if citations else ''} {f'• {venue}' if venue else ''}
                        </span>
                    </div>
                    <h3 style="margin: 12px 0; color: #e2e8f0; font-size: 18px; font-weight: 600;">{title}</h3>
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">{authors}</p>
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">{summary}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if pdf_url and pdf_url != '#':
                        st.link_button("View Paper", pdf_url, use_container_width=True)
                    else:
                        st.button("No PDF Available", disabled=True, use_container_width=True)
                
                with col2:
                    st.link_button(f"View on {source}", abs_url, use_container_width=True)
                
                with col3:
                    if already_saved:
                        st.success("In Library")
                    else:
                        if st.button("Add to Library", key=f"save_{paper_id}_{i}", use_container_width=True):
                            try:
                                new_paper = PaperRecord(
                                    arxiv_id=paper_id,
                                    title=paper['title'],
                                    authors=paper['authors'],
                                    summary=paper.get('summary', ''),
                                    pdf_url=paper.get('pdf_url', ''),
                                    abs_url=paper.get('abs_url', ''),
                                    primary_category=paper.get('category', 'Unknown'),
                                    published=paper.get('published', datetime.now()),
                                    relevance_score=0.95,
                                    is_saved=True
                                )
                                
                                db.session.add(new_paper)
                                db.session.commit()
                                
                                st.session_state.saved_papers.add(paper_id)
                                st.session_state.just_saved = title[:50] + "..."
                                
                                st.rerun()
                                
                            except Exception as e:
                                db.session.rollback()
                                st.error(f"Save failed: {str(e)}")
                
                st.markdown("<br>", unsafe_allow_html=True)

    elif not submit:
        st.markdown("""
        <div class="empty-state-pro">
            <h3>Search Scientific Literature Worldwide</h3>
            <p style="margin-top: 12px;">
                <strong>arXiv:</strong> Physics, Mathematics, Computer Science, Statistics<br>
                <strong>Semantic Scholar:</strong> All sciences including Biology, Medicine, Chemistry<br>
                <strong>PubMed:</strong> Biomedical and Life Sciences
            </p>
            <p style="margin-top: 16px; color: #64748b;">
                Select your data sources above and enter a search query.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    if submit and not query.strip():
        st.warning("Please enter a search query")


elif page == "Training Data":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Training Data Curation
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Label papers to improve model recommendations
    </p>
    """, unsafe_allow_html=True)
    
    try:
        stats = db.get_stats()
    except:
        stats = {}
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Labeled", str(stats.get('labeled_papers', 0)))
    with col2:
        render_metric_card("Relevant", str(stats.get('positive_labels', 0)))
    with col3:
        render_metric_card("Not Relevant", str(stats.get('negative_labels', 0)))
    with col4:
        render_metric_card("Remaining", str(stats.get('unlabeled_papers', 0)))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if stats.get('total_papers', 0) > 0:
        progress = stats['labeled_papers'] / stats['total_papers']
        st.progress(progress)
        st.caption(f"Labeling progress: {progress:.0%}")
    
    st.divider()
    
    try:
        unlabeled = db.get_unlabeled_papers(limit=5)
    except:
        unlabeled = []
    
    if not unlabeled:
        st.markdown("""
        <div class="empty-state-pro">
            <h3>All Papers Labeled</h3>
            <p>You can now train or retrain the classifier model.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<h2 style="font-size: 20px; margin: 0 0 24px; color: #e2e8f0;">Papers Requiring Classification ({len(unlabeled)} shown)</h2>', unsafe_allow_html=True)
        
        for paper in unlabeled:
            render_paper_card(paper)
            col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 3])
            
            with col1:
                if st.button("Relevant", key=f"rel_{paper.arxiv_id}", use_container_width=True, type="primary"):
                    try:
                        db.label_paper(paper.arxiv_id, 1)
                        st.toast("Labeled as relevant")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("Not Relevant", key=f"not_{paper.arxiv_id}", use_container_width=True):
                    try:
                        db.label_paper(paper.arxiv_id, 0)
                        st.toast("Labeled as not relevant")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col3:
                st.link_button("Read Paper", paper.pdf_url or "#", use_container_width=True)
            
            st.divider()

elif page == "Analytics":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Analytics Dashboard
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Insights into your paper collection
    </p>
    """, unsafe_allow_html=True)
    
    try:
        all_papers = db.get_all_papers(limit=2000)
    except:
        all_papers = []
    
    if not all_papers:
        st.warning("No papers in repository")
    else:
        scores = [p.relevance_score or 0 for p in all_papers]
        avg_score = sum(scores) / len(scores)
        high_rel = len([s for s in scores if s >= 0.55])
        low_rel = len([s for s in scores if s < 0.35])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            render_metric_card("Total", str(len(all_papers)))
        with col2:
            render_metric_card("Avg Score", f"{avg_score:.0%}")
        with col3:
            render_metric_card("High Relevance", str(high_rel))
        with col4:
            render_metric_card("Low Relevance", str(low_rel))
        with col5:
            try:
                cat_count = len(db.get_categories())
            except:
                cat_count = 0
            render_metric_card("Categories", str(cat_count))
        
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
            st.markdown('<h3 style="font-size: 18px; margin: 0 0 16px; color: #e2e8f0;">Top 5 Papers by Relevance</h3>', unsafe_allow_html=True)
            top_5 = sorted(all_papers, key=lambda p: p.relevance_score or 0, reverse=True)[:5]
            for i, p in enumerate(top_5, 1):
                score = p.relevance_score or 0
                color, _ = get_score_style(score)
                title_clean = clean_text(p.title or "Untitled")[:50]
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 12px 16px; 
                background: rgba(59, 130, 246, 0.08); border-radius: 8px; margin: 8px 0;
                border-left: 3px solid {color};">
                    <span style="font-size: 18px; font-weight: 700; color: {color}; margin-right: 12px;">#{i}</span>
                    <div style="flex: 1;">
                        <div style="font-size: 14px; font-weight: 500; color: #e2e8f0;">{title_clean}</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 2px;">{score:.0%} relevance</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown('<h3 style="font-size: 20px; margin: 24px 0 16px; color: #e2e8f0;">Score Distribution</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        brackets = [
            ("Excellent (75%+)", len([s for s in scores if s >= 0.75])),
            ("Good (55-74%)", len([s for s in scores if 0.55 <= s < 0.75])),
            ("Fair (35-54%)", len([s for s in scores if 0.35 <= s < 0.55])),
            ("Low (<35%)", len([s for s in scores if s < 0.35]))
        ]
        
        for i, (label, count) in enumerate(brackets):
            with [col1, col2, col3, col4][i]:
                pct = count / len(all_papers) * 100 if all_papers else 0
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.15);
                border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 13px; color: #64748b; margin-bottom: 6px;">{label}</div>
                    <div style="font-size: 32px; font-weight: 700; color: #3b82f6;">{count}</div>
                    <div style="font-size: 12px; color: #475569; margin-top: 4px;">{pct:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

elif page == "Library":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Personal Library
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Your saved papers and reading list
    </p>
    """, unsafe_allow_html=True)
    
    saved_papers = db.get_reading_list()
    
    if not saved_papers:
        st.markdown("""
        <div class="empty-state-pro">
            <h3>Library Empty</h3>
            <p>Search for papers and add them to your library.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"**{len(saved_papers)}** papers in your library")
        
        for paper in saved_papers:
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    render_paper_card(paper)
                
                with col2:
                    if st.button("Remove", key=f"remove_{paper.arxiv_id}", use_container_width=True):
                        db.remove_from_reading_list(paper.arxiv_id)
                        st.toast("Removed from library")
                        st.rerun()
                         

elif page == "Model":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Personalized Ranking Model
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Train and manage your personalized paper recommendation model
    </p>
    """, unsafe_allow_html=True)
    
    stats = db.get_stats()
    labeled_count = stats.get('labeled_papers', 0)
    positive_count = stats.get('positive_labels', 0)
    negative_count = stats.get('negative_labels', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Labeled Papers", str(labeled_count))
    with col2:
        render_metric_card("Relevant", str(positive_count))
    with col3:
        render_metric_card("Not Relevant", str(negative_count))
    with col4:
        status = "Trained" if ml_engine.is_trained else "Untrained"
        render_metric_card("Model Status", status)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Training section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 16px; font-size: 20px;">Train Model</h2>', unsafe_allow_html=True)
    
    can_train = labeled_count >= 5 and positive_count >= 2 and negative_count >= 2
    
    if not can_train:
        st.warning(f"""
        **Additional labels required:**
        - Labeled: {labeled_count}/5 minimum
        - Relevant: {positive_count}/2 minimum  
        - Not Relevant: {negative_count}/2 minimum
        
        Go to **Training Data** to label more papers.
        """)
    else:
        st.success(f"Ready to train with {labeled_count} labeled papers.")
        
        if st.button("Train Model", use_container_width=True, type="primary"):
            with st.spinner("Training model..."):
                result = ml_engine.train(min_samples=5)
            
            if result.get('success'):
                st.balloons()
                
                # Show metrics
                st.success(f"""
                **Training Complete**
                - Accuracy: {result['accuracy']:.1%}
                - Precision: {result['precision']:.1%}
                - F1 Score: {result['f1']:.1%}
                - Training samples: {result['samples']}
                - Evaluation method: {result.get('evaluation_method', 'unknown')}
                """)
                
                # Show reliability warning
                if not result.get('is_reliable', False):
                    st.warning(f"""
                    **⚠️ Model may be unreliable**
                    
                    You have **{result['samples']}** labeled papers ({result['positive_samples']} relevant, {result['negative_samples']} not relevant).
                    
                    For reliable results, you need:
                    - At least **20 labeled papers** total
                    - At least **5 relevant** papers
                    - At least **5 not relevant** papers
                    
                    Current accuracy ({result['accuracy']:.0%}) may not reflect real-world performance.
                    """)
                else:
                    st.info("✓ Model has sufficient training data for reliable predictions.")
                
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
            st.markdown('<h3 style="color: #e2e8f0; margin: 0 0 16px; font-size: 18px;">Model Metrics</h3>', unsafe_allow_html=True)
            
            prefs = db.get_preferences()
            if prefs.model_accuracy:
                st.metric("Accuracy", f"{prefs.model_accuracy:.1%}")
            if prefs.model_last_trained:
                st.metric("Last Trained", prefs.model_last_trained.strftime("%Y-%m-%d %H:%M"))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #e2e8f0; margin: 0 0 16px; font-size: 18px;">Learned Features</h3>', unsafe_allow_html=True)
            
            model_state = db.get_active_model()
            if model_state:
                import json
                try:
                    top_pos = json.loads(model_state.top_positive_features or '[]')
                    top_neg = json.loads(model_state.top_negative_features or '[]')
                    
                    st.markdown("**Positive indicators:**")
                    for item in top_pos[:5]:
                        st.markdown(f"- {item['word']}")
                    
                    st.markdown("**Negative indicators:**")
                    for item in top_neg[:5]:
                        st.markdown(f"- {item['word']}")
                except:
                    pass
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <h2 style="font-size: 20px; margin: 24px 0 16px; color: #e2e8f0;">Model Recommendations</h2>
        <p style="color: #64748b; margin-bottom: 16px;">Papers ranked by predicted relevance</p>
        """, unsafe_allow_html=True)
        
        recommendations = ml_engine.get_recommendations(limit=5)
        
        if recommendations:
            for idx, paper in enumerate(recommendations):
                pred_score = ml_engine.predict_relevance(paper)
                
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
                            <div style="background: {color}; color: white; padding: 10px 14px; 
                                        border-radius: 8px; text-align: center; font-weight: 600;">
                                {pred_score:.0%}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.write(clean_text(paper.summary)[:300] + "...")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.link_button("View PDF", paper.pdf_url or "#", use_container_width=True)
                    with col2:
                        if st.button("Relevant", key=f"ai_rel_{paper.arxiv_id}_{idx}"):
                            db.label_paper(paper.arxiv_id, 1)
                            st.toast("Labeled as relevant")
                            st.rerun()
                    with col3:
                        if st.button("Not Relevant", key=f"ai_not_{paper.arxiv_id}_{idx}"):
                            db.label_paper(paper.arxiv_id, 0)
                            st.toast("Labeled as not relevant")
                            st.rerun()
                    with col4:
                        if is_already_saved:
                            st.success("Saved")
                        else:
                            if st.button("Save", key=f"ai_save_{paper.arxiv_id}_{idx}", use_container_width=True):
                                success = db.save_to_reading_list(paper.arxiv_id)
                                if success:
                                    st.toast("Added to library")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Failed to save")
                    
                    st.divider()
        else:
            st.info("Label more papers to generate personalized recommendations.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Re-score All Papers", use_container_width=True):
            with st.spinner("Scoring papers..."):
                scores = ml_engine.score_all_papers()
            st.success(f"Updated scores for {len(scores)} papers")
    
    # Research interests
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 16px; font-size: 20px;">Research Interest Profile</h2>', unsafe_allow_html=True)
    
    interests = db.get_user_interests()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top Categories**")
        if interests['categories']:
            for cat, count in list(interests['categories'].items())[:8]:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 12px; 
                            background: rgba(59, 130, 246, 0.08); border-radius: 6px; margin: 6px 0;">
                    <span style="color: #e2e8f0;">{cat}</span>
                    <span style="color: #3b82f6; font-weight: 600;">{count}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Label papers to see category preferences")
    
    with col2:
        st.markdown("**Top Keywords**")
        if interests['keywords']:
            keywords_html = ' '.join([
                f'<span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 4px 12px; border-radius: 16px; margin: 3px; display: inline-block; font-size: 13px;">{kw}</span>'
                for kw in interests['keywords'][:15]
            ])
            st.markdown(keywords_html, unsafe_allow_html=True)
        else:
            st.info("Label papers to see keyword preferences")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Settings":
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px; margin: 40px 0 16px;'>
        Settings
    </h1>
    <p style='text-align: center; font-size: 16px; color: #64748b; margin-bottom: 40px;'>
        Configure your Research Intelligence Platform
    </p>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Email Digest", "Notifications", "Database", "Commands", "Appearance"])
    
    # =========================================================================
    # TAB 1: EMAIL DIGEST
    # =========================================================================
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 16px; font-size: 20px;">Email Digest Configuration</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; margin-bottom: 16px;">Receive curated paper recommendations via email</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        prefs = db.get_preferences()
        
        with st.form("email_settings"):
            st.markdown("### Email Address")
            email = st.text_input("Email", value=prefs.email or "", placeholder="your@email.com", label_visibility="collapsed")
            
            st.markdown("### Digest Schedule")
            col1, col2 = st.columns(2)
            with col1:
                freq_options = ["none", "daily", "weekly"]
                current_freq = prefs.digest_frequency if prefs.digest_frequency in freq_options else "weekly"
                frequency = st.selectbox("Frequency", freq_options, index=freq_options.index(current_freq))
            with col2:
                if frequency == "weekly":
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    digest_day = st.selectbox("Day", days, index=prefs.digest_day or 0)
                    digest_day_idx = days.index(digest_day)
                else:
                    digest_day_idx = 0
            
            st.markdown("### Digest Options")
            col1, col2 = st.columns(2)
            with col1:
                # Convert stored decimal (0.5) to percentage (50) for display
                current_pct = int((prefs.min_relevance_score or 0.5) * 100)
                min_score_pct = st.slider("Minimum relevance score", 0, 100, current_pct, 5, format="%d%%")
                # Convert back to decimal for storage
                min_score = min_score_pct / 100.0
            with col2:
                max_papers = st.number_input("Maximum papers per digest", 5, 30, prefs.max_papers_per_digest or 10)
            
            st.markdown("### SMTP Configuration")
            st.info("For Gmail: Use an App Password. [Learn more](https://support.google.com/accounts/answer/185833)")
            
            col1, col2 = st.columns(2)
            with col1:
                smtp_host = st.text_input("SMTP Host", value=prefs.smtp_host or "smtp.gmail.com")
                smtp_user = st.text_input("SMTP Username", value=prefs.smtp_user or "")
            with col2:
                smtp_port = st.number_input("SMTP Port", value=prefs.smtp_port or 587)
                smtp_password = st.text_input("SMTP Password", type="password", value="")
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("Save Settings", use_container_width=True, type="primary")
            with col2:
                test_btn = st.form_submit_button("Send Test Email", use_container_width=True)
        
        if save_btn:
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
            
            st.success("Settings saved")

        
        if test_btn:
            email = clean_form_input(email)
            
            if not email:
                st.error("Please enter your email address")
            elif not (smtp_user or prefs.smtp_user) or not (smtp_password or prefs.smtp_password):
                st.error("Please configure SMTP settings")
            else:
                if smtp_user and smtp_password:
                    email_service.configure(smtp_host, smtp_port, smtp_user, smtp_password)
                
                with st.spinner("Sending test email..."):
                    success, message = email_service.send_test_email(email)
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Send Digest Manually")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            days_back = st.selectbox("Papers from last", [1, 3, 7, 14, 30], index=2)
        with col2:
            if st.button("Send Digest Now", use_container_width=True):
                prefs = db.get_preferences()
                if not prefs.email:
                    st.error("Please set your email address")
                else:
                    papers = db.get_papers_for_digest(since_days=days_back)
                    if not papers:
                        st.warning("No relevant papers found")
                    else:
                        with st.spinner(f"Sending digest with {len(papers)} papers..."):
                            success, message = email_service.send_digest(prefs.email, papers, "manual")
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Digest History")
        
        history = db.get_digest_history(limit=10)
        if history:
            for h in history:
                status_icon = "✓" if h.status == "sent" else "✗"
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 10px 14px;
                            background: rgba(59, 130, 246, 0.08); border-radius: 6px; margin: 6px 0;">
                    <span style="color: #e2e8f0;">{status_icon} {h.digest_type.title()} - {h.paper_count} papers</span>
                    <span style="color: #64748b;">{h.sent_at.strftime('%Y-%m-%d %H:%M')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No digests sent yet")
    
    # =========================================================================
    # TAB 2: NOTIFICATIONS
    # =========================================================================
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 16px; font-size: 20px;">Notification Settings</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        prefs = db.get_preferences()
        
        notify_high = st.toggle("Notify for high-relevance papers (90%+)", value=prefs.notify_high_relevance)
        auto_train = st.toggle("Auto-train model when new labels added", value=prefs.auto_train)
        
        if st.button("Save Notification Settings"):
            db.update_preferences(notify_high_relevance=notify_high, auto_train=auto_train)
            st.success("Saved")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Category Tracking")
        st.info("Select categories to focus your digest on specific research areas")
        
        all_categories = db.get_categories()
        tracked = prefs.get_tracked_categories()
        
        selected_cats = st.multiselect(
            "Tracked Categories",
            all_categories,
            default=[c for c in tracked if c in all_categories]
        )
        
        if st.button("Save Tracked Categories"):
            prefs.set_tracked_categories(selected_cats)
            db.session.commit()
            st.success(f"Tracking {len(selected_cats)} categories")
    
    # =========================================================================
    # TAB 3: DATABASE
    # =========================================================================
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 16px; font-size: 20px;">Database Status</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        stats = db.get_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Papers", f"{stats.get('total_papers', 0):,}")
        with col2:
            render_metric_card("Labeled", f"{stats.get('labeled_papers', 0):,}")
        with col3:
            render_metric_card("Saved", f"{stats.get('saved_papers', 0):,}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**Database Path:** `{DB_PATH}`")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Model Status")
        
        model_state = db.get_active_model()
        if model_state:
            st.success(f"""
            **Model Active**
            - Trained: {model_state.trained_at.strftime('%Y-%m-%d %H:%M') if model_state.trained_at else 'Unknown'}
            - Samples: {model_state.training_samples}
            - Accuracy: {f"{model_state.accuracy:.1%}" if model_state.accuracy else 'N/A'}
            """)
        else:
            st.warning("No trained model. Go to Model page to train.")
    
    # =========================================================================
    # TAB 4: COMMANDS
    # =========================================================================
    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #e2e8f0; margin: 0 0 16px; font-size: 20px;">Command Reference</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        commands = [
            ("Fetch New Papers", "python src/daily_run.py", "Fetches latest papers from arXiv"),
            ("Run Scheduler", "python src/scheduler.py", "Runs background digest scheduler"),
        ]
        
        for title, cmd, desc in commands:
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.15);
                        border-radius: 12px; padding: 20px; margin: 12px 0;">
                <div style="font-weight: 600; color: #e2e8f0; font-size: 16px; margin-bottom: 10px;">{title}</div>
                <code style="display: block; background: #0f172a; color: #60a5fa; padding: 12px 16px; 
                            border-radius: 8px; font-size: 14px; margin: 10px 0;">{cmd}</code>
                <div style="font-size: 14px; color: #64748b; margin-top: 8px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
        # =========================================================================
    # TAB 5: APPEARANCE
    # =========================================================================
    with tab5:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="margin: 0 0 16px; font-size: 20px;">Appearance</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### Theme")
        
        current_theme = st.session_state.theme
        
        col1, col2 = st.columns(2)
        
        with col1:
            dark_label = "✓ Dark" if current_theme == 'dark' else "Dark"
            if st.button(
                dark_label,
                use_container_width=True,
                type="primary" if current_theme == 'dark' else "secondary"
            ):
                st.session_state.theme = 'dark'
                st.rerun()
        
        with col2:
            light_label = "✓ Light" if current_theme == 'light' else "Light"
            if st.button(
                light_label,
                use_container_width=True,
                type="primary" if current_theme == 'light' else "secondary"
            ):
                st.session_state.theme = 'light'
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if current_theme == 'dark':
            st.info("**Dark theme active** — Optimized for low-light environments and reduced eye strain.")
        else:
            st.info("**Light theme active** — High contrast for maximum readability in bright environments.")

# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.markdown(f"""
<div style="text-align: center; padding: 24px 0; color: #475569; font-size: 13px;">
    Research Intelligence Platform · {datetime.now().year}
</div>
""", unsafe_allow_html=True)
