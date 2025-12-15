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

        /* Main layout spacing */
        [data-testid="stMainBlockContainer"]{ padding-top: 14px; }
        </style>
        """
        ).strip(),
        unsafe_allow_html=True,
    )
