import streamlit as st
from textwrap import dedent


def apply_wildflix_theme():
    st.markdown(
        dedent(
            """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        :root{
          --bg:#0B0F17;
          --surface:#141C2B;
          --border:#25324A;
          --text:#EAF0FF;
          --muted:#A7B3CC;
          --primary:#FFB020;
          --success:#2BD576;
          --danger:#FF3B3B;
          --radius:14px;
          --radius-btn:12px;
          --shadow:0 10px 28px rgba(0,0,0,.35);
        }

        .stApp{
          background:var(--bg);
          color:var(--text);
          font-family:'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        }

        /* Headings */
        h1{ font-size:36px; font-weight:800; color:var(--text); letter-spacing:.2px; }
        h2{ font-size:24px; font-weight:700; color:var(--text); letter-spacing:.2px; }
        h3{ font-size:20px; font-weight:700; color:var(--text); letter-spacing:.2px; }

        /* Body text */
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li{
          color:var(--muted);
        }
        label{ color:var(--muted) !important; font-size:12px !important; }

        /* Sidebar */
        section[data-testid="stSidebar"]{
          background:#080C14;
          border-right:1px solid var(--border);
        }

        /* Logged-in user line (sidebar) */
        .wf-connected-as{
          margin: 8px 0 10px 0;
          padding: 10px 12px;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius-btn);
          text-align: center;
          font-weight: 700;
          color: var(--muted);
        }
        .wf-connected-as__name{
          color: var(--text);
          font-weight: 800;
        }

        /* Inputs */
        input, textarea{
          background:var(--surface) !important;
          color:var(--text) !important;
          border:1px solid var(--border) !important;
          border-radius:var(--radius-btn) !important;
        }
        div[data-baseweb="select"] > div{
          background:var(--surface) !important;
          color:var(--text) !important;
          border:1px solid var(--border) !important;
          border-radius:var(--radius-btn) !important;
        }

        /* Buttons */
        button[data-testid="baseButton-primary"]{
          background:var(--primary) !important;
          color:#0B0F17 !important;
          border:0 !important;
          border-radius:var(--radius-btn) !important;
          padding:10px 14px !important;
          font-weight:800 !important;
        }
        
        button[data-testid="baseButton-primary"]:hover{
          filter:brightness(1.05);
          transform:translateY(-1px);
        }
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-tertiary"]{
          background:transparent !important;
          color:var(--text) !important;
          border:1px solid var(--border) !important;
          border-radius:var(--radius-btn) !important;
          padding:10px 14px !important;
          font-weight:700 !important;
        }
        button[data-testid="baseButton-tertiary"]{
          color:var(--muted) !important;
        }

        /* Modal / Dialog Styling */
        div[data-testid="stDialog"] {
            background-color: var(--surface) !important;
            color: var(--text) !important;
        }
        div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] p {
             color: var(--text) !important; /* Ensure readable text in modal */
        }

        /* Main layout spacing */
        [data-testid="stMainBlockContainer"]{ padding-top: 14px; }
        
        /* --- COMPONENT STYLES (Moved from ui_components.py) --- */
        
        /* v=FORCE_UPDATE_FINAL_72PX_HEART */
        /* Masque le menu multipage par defaut */
        [data-testid="stSidebarNav"] { display: none; }

        /* Scroll horizontal pour les rangées */
        [class*="st-key-wf-scroll-"] div[data-testid="stHorizontalBlock"] {
          overflow-x: auto;
          flex-wrap: nowrap;
          gap: 16px;
          padding-bottom: 8px;
        }
        [class*="st-key-wf-scroll-"] div[data-testid="column"],
        [class*="st-key-wf-scroll-"] div[data-testid="stColumn"] {
          min-width: 260px;
          max-width: 260px; /* Strict sizing */
          flex: 0 0 260px;
        }

        /* Cartes films - Strict Fixed Size (Increased) */
        [class*="st-key-wf_card_"] {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          box-shadow: var(--shadow);
          padding: 12px;
          width: 260px !important;
          min-width: 260px !important;
          max-width: 260px !important;
          height: 640px !important;  /* Reduced from 680px to 640px per user request */
          min-height: 640px !important;
          max-height: 640px !important;
          display: flex !important;
          flex-direction: column !important;
          justify-content: flex-start !important;
          position: relative;
          overflow: hidden !important;
        }

        /* Container poster - ALLOW OVERFLOW for Heart */
        [class*="st-key-wf_poster_wrap_"] {
           position: relative !important;
           width: 100% !important;
           height: 320px !important;
           margin-bottom: 12px !important;
           flex-shrink: 0 !important;
           overflow: visible !important; /* CRITICAL for Heart overlap */
        }

        /* Poster Buttons */
        [class*="st-key-wf_poster_btn_"] button {
          height: 320px !important;
          width: 100% !important;
          padding: 0;
          border-radius: 12px;
          background-size: contain !important;
          background-position: center;
          background-repeat: no-repeat;
          background-color: var(--surface);
          border: 1px solid var(--border);
        }
        [class*="st-key-wf_poster_btn_"] button > div { opacity: 0; }
        
        /* Custom Metadata Layout - Natural Flow with Pinned Footer */
        [class*="st-key-wf_card_"] {
             /* Ensure the card itself is a flex container so we can use flex-grow inside */
             display: flex !important;
             flex-direction: column !important;
        }
        
        /* The container for all our custom HTML metadata */
        .wf-meta-container {
            display: flex;
            flex-direction: column;
            flex: 1; /* Grow to fill all available space in the card */
            gap: 4px; /* Consistent small gap between natural rows */
            margin-top: 4px;
        }

        .wf-meta-row {
            font-size: 13px !important;
            line-height: 1.4 !important;
            color: var(--muted);
            width: 100%;
        }

        /* Director and Actors: Allow 2 lines, but NO forced minimum height (Natural spacing) */
        .wf-meta-text {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            white-space: normal;
            overflow: hidden;
            text-overflow: ellipsis;
            /* No min-height: purely content driven */
        }
        
        /* Duration: Pinned to the very bottom of the card */
        .wf-meta-duration {
            margin-top: auto !important; /* Pushes this element to the bottom */
            padding-top: 8px; /* Visual separation from content */
            font-weight: 600;
            color: var(--text-color);
            border-top: 1px solid var(--border); /* Optional: nice separator */
        }
        
        /* Special style for Title Button - 2 LINES ALLOWED */
        [class*="st-key-wf_card_"] button[data-testid="baseButton-secondary"] {
             display: -webkit-box !important;
             -webkit-line-clamp: 2 !important; 
             -webkit-box-orient: vertical !important;
             white-space: normal !important; 
             overflow: hidden !important;
             text-overflow: ellipsis !important;
             width: 100% !important;
             text-align: left !important;
             font-weight: 700 !important;
             font-size: 16px !important;
             line-height: 1.2 !important;
             border: none !important;
             padding: 0 !important;
             margin-bottom: 8px !important;
             height: auto !important;
             min-height: 40px !important;
        }
        
        /* Typography Truncation override for other markdown */
        [class*="st-key-wf_card_"] div[data-testid="stMarkdownContainer"] p {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            margin-bottom: 4px !important;
            font-size: 14px !important;
            line-height: 1.4 !important;
        }

        /* --- NUCLEAR OVERRIDES --- */
        
        /* 1. BUTTON TEXT COLOR: Force Black on Primary */
        button[kind="primary"],
        button[data-testid="baseButton-primary"],
        button[data-testid="stBaseButton-primary"],
        html body button[data-testid="baseButton-primary"] * {
             color: #000000 !important;
             fill: #000000 !important;
             -webkit-text-fill-color: #000000 !important;
             font-weight: 800 !important;
        }

        /* 2. FLAGS: Force Size 48px & Visibility */
        [class*="st-key-side_lang_"] button,
        [class*="st-key-side_lang_"] button div,
        [class*="st-key-side_lang_"] button p,
        [class*="st-key-side_lang_"] button span {
             font-size: 48px !important;
             min-height: 54px !important;
             height: auto !important;
             background: transparent !important;
             border: none !important;
             opacity: 1 !important;
             visibility: visible !important;
             color: #ffffff !important;
             line-height: 1.1 !important;
        }

        /* --- HEART OVERLAY (MOVED TO END FOR PRECEDENCE) --- */
        [class*="st-key-wf_fav_overlay_"] {
            position: absolute !important;
            top: auto !important;
            bottom: 0px !important;
            left: 50% !important;
            transform: translate(-50%, 50%) !important;
            right: auto !important;
            z-index: 999 !important; 
            width: auto !important;
            height: auto !important;
        }
        [class*="st-key-wf_fav_overlay_"] button {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            width: auto !important;
            height: auto !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [class*="st-key-wf_fav_overlay_"] button:hover {
             background: transparent !important;
             transform: scale(1.1);
        }
        
        /* SUPER SPECIFIC OVERRIDE + ORDER FIX + SCALE FAILSAFE */
        html body [class*="st-key-wf_fav_overlay_"] button,
        html body [class*="st-key-wf_fav_overlay_"] button p,
        html body [class*="st-key-wf_fav_overlay_"] button span,
        html body [class*="st-key-wf_fav_overlay_"] button div,
        html body [class*="st-key-wf_fav_overlay_"] button * {
            color: var(--danger) !important; 
            -webkit-text-fill-color: var(--danger) !important;
            fill: var(--danger) !important;
            font-size: 48px !important; /* Base size */
            font-weight: 400 !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
            text-shadow: 0 4px 10px rgba(0,0,0,0.8) !important;
            transform: scale(1.2) !important; /* Reduced from 1.5 */
            transform-origin: center center !important;
        }   
        </style>
        """
        ).strip(),
        unsafe_allow_html=True,
    )
