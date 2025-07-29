import streamlit as st
import pandas as pd
import datetime
import os
from utils.config import CONFIG
from utils.validators import validate_slug, validate_days, validate_dates, validate_time
from utils.data_processor import process_class_data, load_course_master_data, save_course_master_data
from utils.export import export_to_csv
import re
import json
import traceback
from utils.logger import setup_logger, log_error

# Custom theme configuration
st.set_page_config(
    page_title="Class Creator",
    layout="wide"
)

# Custom CSS with black background and rainbow gradient fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main background and text colors */
    .stApp {
        background: #000000;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Rainbow gradient keyframes */
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Headers with rainbow gradient */
    h1, h2, h3, .st-emotion-cache-10trblm {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: rainbow 3s ease infinite;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
    }
    
    /* Primary buttons with rainbow gradient */
    .stButton > button {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        text-shadow: none !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 12px 40px rgba(255, 255, 255, 0.4) !important;
        filter: brightness(1.2) !important;
    }
    
    /* Form submit buttons (login, submit request, etc.) */
    .stForm button, .stForm input[type="submit"], button[kind="primary"], button[kind="secondary"] {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        text-shadow: none !important;
        cursor: pointer !important;
    }
    .stForm button:hover, .stForm input[type="submit"]:hover, button[kind="primary"]:hover, button[kind="secondary"]:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 12px 40px rgba(255, 255, 255, 0.4) !important;
        filter: brightness(1.2) !important;
    }
    
    /* Specific targeting for form submit buttons */
    div[data-testid="stForm"] button {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        text-shadow: none !important;
    }
    div[data-testid="stForm"] button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 12px 40px rgba(255, 255, 255, 0.4) !important;
        filter: brightness(1.2) !important;
    }
    
    /* Download button with rainbow gradient */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.3) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 12px 40px rgba(255, 255, 255, 0.4) !important;
        filter: brightness(1.2) !important;
    }
    
    /* Success messages with rainbow gradient */
    .stSuccess {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.3) !important;
        font-weight: 600 !important;
    }
    
    /* Error messages with red gradient */
    .stError {
        background: linear-gradient(45deg, #ff1744, #ff5722, #ff9800, #ff1744) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #ffffff !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 8px 32px rgba(255, 23, 68, 0.4) !important;
        font-weight: 600 !important;
    }
    
    /* Warning messages with orange gradient */
    .stWarning {
        background: linear-gradient(45deg, #ff9800, #ff5722, #ffeb3b, #ff9800) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 8px 32px rgba(255, 152, 0, 0.4) !important;
        font-weight: 600 !important;
    }
    
    /* Info messages with blue gradient */
    .stInfo {
        background: linear-gradient(45deg, #2196f3, #03a9f4, #00bcd4, #2196f3) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #ffffff !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 8px 32px rgba(33, 150, 243, 0.4) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #000000 100%);
        border-right: 2px solid #333333;
    }
    
    /* Input fields with neon glow */
    .stTextInput > div > div > input {
        background: rgba(20, 20, 20, 0.8) !important;
        border: 2px solid #333333 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border: 2px solid transparent !important;
        background: linear-gradient(#1a1a1a, #1a1a1a) padding-box, linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) border-box !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: #333333 !important;
        border: 2px solid #666666 !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox > div > div:focus-within {
        border: 2px solid transparent !important;
        background: linear-gradient(#333333, #333333) padding-box, linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) border-box !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Select box text and options */
    .stSelectbox > div > div > div {
        background: #333333 !important;
        color: #ffffff !important;
    }
    .stSelectbox option {
        background: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Multi-select */
    .stMultiSelect > div > div {
        background: #333333 !important;
        border: 2px solid #666666 !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    .stMultiSelect > div > div:focus-within {
        border: 2px solid transparent !important;
        background: linear-gradient(#333333, #333333) padding-box, linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) border-box !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Multi-select dropdown options */
    .stMultiSelect > div > div > div {
        background: #333333 !important;
        color: #ffffff !important;
    }
    .stMultiSelect option {
        background: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Course code dropdown options - black background like date input */
    .stMultiSelect div[role="listbox"] {
        background: #000000 !important;
        border: 2px solid #333333 !important;
    }
    .stMultiSelect div[role="option"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    .stMultiSelect div[role="option"]:hover {
        background: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Course code multiselect dropdown styling */
    .stMultiSelect div[data-baseweb="select"] > div > div {
        background: #000000 !important;
    }
    .stMultiSelect div[data-baseweb="select"] div[role="listbox"] div {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Additional course code dropdown targeting */
    .stMultiSelect div[data-baseweb="popover"] {
        background: #000000 !important;
    }
    .stMultiSelect div[data-baseweb="popover"] > div {
        background: #000000 !important;
        border: 2px solid #333333 !important;
    }
    .stMultiSelect li {
        background: #000000 !important;
        color: #ffffff !important;
    }
    .stMultiSelect li:hover {
        background: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Multi-select selected items */
    .stMultiSelect span {
        background: #555555 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }
    
    /* Date input */
    .stDateInput > div > div > input {
        background: #000000 !important;
        border: 2px solid #333333 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        color: #ffffff !important;
    }
    .stDateInput > div > div > input:focus {
        border: 2px solid transparent !important;
        background: linear-gradient(#000000, #000000) padding-box, linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) border-box !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Date picker popup */
    .stDateInput div[data-baseweb="calendar"] {
        background: #000000 !important;
        border: 1px solid #333333 !important;
        color: #ffffff !important;
    }
    
    /* Time input with black text */
    .stTimeInput > div > div > input {
        background: #ffffff !important;
        border: 2px solid #333333 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        color: #000000 !important;
    }
    .stTimeInput > div > div > input:focus {
        border: 2px solid transparent !important;
        background: linear-gradient(#ffffff, #ffffff) padding-box, linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) border-box !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Time picker popup - black text on light background */
    .stTimeInput div[data-baseweb="popover"] {
        background: #f0f0f0 !important;
    }
    .stTimeInput div[data-baseweb="popover"] > div {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput div[data-baseweb="popover"] div {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput div[data-baseweb="popover"] span {
        color: #000000 !important;
    }
    
    /* Time options in the picker */
    .stTimeInput div[role="listbox"] {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput div[role="option"] {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput div[role="option"]:hover {
        background: #e0e0e0 !important;
        color: #000000 !important;
    }
    
    /* Time picker specific elements */
    .stTimeInput li {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput li:hover {
        background: #e0e0e0 !important;
        color: #000000 !important;
    }
    
    /* Additional time picker targeting */
    .stTimeInput div[data-baseweb="select"] div {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput div[data-baseweb="menu"] {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput div[data-baseweb="menu"] div {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Time picker dropdown menu */
    .stTimeInput [role="menuitem"] {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput [role="menuitem"]:hover {
        background: #e0e0e0 !important;
        color: #000000 !important;
    }
    
    /* More comprehensive time picker targeting */
    .stTimeInput div[data-baseweb="popover"] * {
        color: #000000 !important;
    }
    .stTimeInput div[data-baseweb="menu"] * {
        color: #000000 !important;
        background: #f0f0f0 !important;
    }
    .stTimeInput [role="presentation"] {
        background: #f0f0f0 !important;
    }
    .stTimeInput [role="presentation"] * {
        color: #000000 !important;
        background: #f0f0f0 !important;
    }
    
    /* Target all text in time picker */
    .stTimeInput div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    .stTimeInput div[data-baseweb="select"] div span {
        color: #000000 !important;
    }
    
    /* Streamlit specific time picker classes */
    .stTimeInput [class*="option"] {
        background: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stTimeInput [class*="option"]:hover {
        background: #e0e0e0 !important;
        color: #000000 !important;
    }
    
    /* Universal text override for time picker */
    .stTimeInput div[role="listbox"] * {
        color: #000000 !important;
    }
    .stTimeInput div[role="option"] * {
        color: #000000 !important;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background: rgba(20, 20, 20, 0.8) !important;
        border: 2px solid #333333 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }
    .stTextArea > div > div > textarea:focus {
        border: 2px solid transparent !important;
        background: linear-gradient(#1a1a1a, #1a1a1a) padding-box, linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) border-box !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Checkboxes with white labels */
    .stCheckbox > label {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Checkbox labels - white text */
    .stCheckbox label {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        background: none !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    /* Meeting Days section styling */
    .stCheckbox div label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Radio buttons with rainbow labels */
    .stRadio > label {
        font-family: 'Inter', sans-serif !important;
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: rainbow 4s ease infinite;
        font-weight: 500 !important;
    }
    
    /* Specific radio button styling for forms and manage courses */
    .stRadio label, .stRadio > div > label, .stRadio div label {
        color: #ff3333 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        background: none !important;
        -webkit-text-fill-color: #ff3333 !important;
    }
    
    /* Radio button options text */
    .stRadio > div > div > div > label {
        color: #ff3333 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        background: none !important;
        -webkit-text-fill-color: #ff3333 !important;
    }
    
    /* Radio button container labels */
    .stRadio > div > label > div {
        color: #ff3333 !important;
    }
    
    /* Cards/containers with dark glass effect */
    div.stMarkdown {
        background: rgba(30, 30, 30, 0.7);
        backdrop-filter: blur(20px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Expander with dark theme */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 30, 0.8) !important;
        border-radius: 12px !important;
        border: 1px solid #333333 !important;
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }
    
    /* Tabs with rainbow active state */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 30, 30, 0.8);
        border-radius: 12px;
        border: 1px solid #333333;
        padding: 0.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: #cccccc !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        animation: rainbow 3s ease infinite !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Links with rainbow effect */
    a {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: rainbow 3s ease infinite;
        text-decoration: none !important;
        font-weight: 600 !important;
    }
    a:hover {
        filter: brightness(1.3) !important;
        text-decoration: underline !important;
    }

    /* Custom header banner - Epic rainbow style */
    .header-banner {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        animation: rainbow 3s ease infinite;
        padding: 2.5rem;
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    .header-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        animation: shine 2s ease-in-out infinite;
    }
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    .header-banner .logo-text {
        display: flex;
        align-items: center;
        gap: 2rem;
        position: relative;
        z-index: 1;
    }
    .header-banner .logo {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        color: #000000;
        text-decoration: none;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    .header-banner .title {
        color: #000000 !important;
        margin: 0;
        padding: 0;
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    /* Form styling with dark theme */
    .stForm {
        background: rgba(30, 30, 30, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        padding: 2rem;
    }

    /* Temporary success message with rainbow */
    .temp-success-message {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        animation: rainbow 3s ease infinite;
        color: #000000;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.3);
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    .temp-success-message.fade-out {
        background: transparent;
        color: #666666;
    }
    
    /* Column spacing */
    .row-widget.stHorizontal {
        gap: 1rem;
    }
    
    /* Labels with rainbow effect */
    label {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000) !important;
        background-size: 400% 400% !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        animation: rainbow 4s ease infinite !important;
        font-weight: 600 !important;
    }
    
    /* Paragraphs and regular text */
    p, div, span {
        color: #ffffff !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        animation: rainbow 3s ease infinite;
        border-radius: 6px;
    }
    ::-webkit-scrollbar-thumb:hover {
        filter: brightness(1.2);
    }
    </style>
""", unsafe_allow_html=True)

# Display app header with text-based logo
st.markdown("""
    <div class="header-banner">
        <div class="logo-text">
            <span class="logo">nerdy</span>
            <span class="title">Class Creator</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    st.session_state.requests = pd.DataFrame(columns=[
        'slug', 'meeting_days', 'start_date', 'end_date', 'start_time',
        'requested_by', 'request_date', 'status'
    ])

setup_logger()

def authenticate():
    """
    Authenticate user with username and password.
    
    Returns:
        True if authenticated, False otherwise
    """
    if st.session_state.authenticated:
        return True
    
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # Check if username exists in config
            if username in CONFIG['users']:
                # Check if password matches
                if password == CONFIG['users'][username]['password']:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = CONFIG['users'][username]['role']
                    st.rerun()
                else:
                    st.error("Invalid password.")
            else:
                st.error("Invalid username.")
    
    return st.session_state.authenticated

def main():
    # Display app header
    st.markdown("<h1 style='color: green;'>Class Creator</h1>", unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not authenticate():
        return
    
    # Create tabs based on user role
    if st.session_state.user_role == 'admin':
        tab1, tab2, tab3, tab4 = st.tabs([
            "Request New Class", 
            "Approve/Deny Requests", 
            "Export Data",
            "Manage Courses"
        ])
    else:
        tab1, tab2 = st.tabs([
            "Request New Class", 
            "My Requests"
        ])
    
    # Tab 1: Request New Class (available to all authenticated users)
    with tab1:
        st.header("Request New Class")
        
        # Add a success message container that will be shown after submission
        success_container = st.empty()
        
        # Create a form key that can be changed to reset the form
        form_key = "class_request_form"
        if "form_reset_counter" not in st.session_state:
            st.session_state.form_reset_counter = 0
        
        # Create a callback to update end_date when start_date changes
        def update_end_date():
            st.session_state.end_date_selected = st.session_state.start_date_selected
        
        with st.form(f"{form_key}_{st.session_state.form_reset_counter}"):
            st.write(
                "Please select one or more course codes from the menu below, then choose the meeting day(s), start and end dates, and start time for the class."
            )
            st.write(
                "You can type to search for a course code. Hold Ctrl (or Cmd on Mac) to select multiple courses. Maximum 100 courses per request."
            )
            
            # Load all course codes from course_master.json
            course_master = load_course_master_data()
            all_course_codes = list(course_master.keys())

            # Multi-select dropdown for course codes
            selected_slugs = st.multiselect(
                "Select Course Code(s)",
                options=all_course_codes,
                help="Type to search. Hold Ctrl (or Cmd on Mac) to select multiple.",
            )

            # Show a message if no matches found (when user types and nothing matches)
            if not all_course_codes:
                st.warning("No course codes available. Please add courses in 'Manage Courses'.")
            elif selected_slugs == [] and st.session_state.get("form_submitted", False):
                st.info("No matches found.")
            
            # Days of week
            st.write("Meeting Days")
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                monday = st.checkbox("Mon")
            with col2:
                tuesday = st.checkbox("Tue")
            with col3:
                wednesday = st.checkbox("Wed")
            with col4:
                thursday = st.checkbox("Thu")
            with col5:
                friday = st.checkbox("Fri")
            with col6:
                saturday = st.checkbox("Sat")
            with col7:
                sunday = st.checkbox("Sun")
            
            meeting_days = []
            if monday: meeting_days.append("Monday")
            if tuesday: meeting_days.append("Tuesday")
            if wednesday: meeting_days.append("Wednesday")
            if thursday: meeting_days.append("Thursday")
            if friday: meeting_days.append("Friday")
            if saturday: meeting_days.append("Saturday")
            if sunday: meeting_days.append("Sunday")
            
            # Date range
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.date.today(),
                    key="start_date_selected"
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=start_date,  # Initialize with start_date
                    min_value=start_date,
                    key="end_date_selected"
                )
            
            # Time - default to noon
            default_time = datetime.time(12, 0)  # 12:00 PM
            start_time = st.time_input("Start Time (Central)", value=default_time)
            
            # --- Excluded Meeting Dates logic (hidden from UI) ---
            # The following UI elements are hidden, but the logic is preserved for future use.

            # st.write("Excluded Meeting Dates (holidays, etc.)")

            # if not (has_meeting_days and has_date_range):
            #     st.info("Please select at least one meeting day and a valid date range to enable excluded dates selection.")

            # excluded_dates = st.multiselect(
            #     "Select dates when class will NOT meet",
            #     options=excluded_date_options,
            #     format_func=lambda x: x.strftime('%Y-%m-%d (%A)'),
            #     help="Select dates when the class will not meet (e.g., holidays)",
            #     disabled=not (has_meeting_days and has_date_range)
            # )

            # Instead, just set excluded_dates to an empty list for now (or keep the logic if you want to use it in the backend)
            excluded_dates = []
            
            submitted = st.form_submit_button("Submit Request")
            
            if submitted:
                # Mark that the form was submitted (for "no matches found" logic)
                st.session_state["form_submitted"] = True

                slugs = selected_slugs
                # Process multiple course codes
                if len(slugs) > 100:
                    st.error("Maximum of 100 course codes allowed. Please reduce the number of course codes.")
                    return
                
                # Validate inputs
                if not slugs:
                    st.error("Please select at least one course code.")
                    return
                
                if not validate_days(meeting_days):
                    st.error("Please select at least one meeting day.")
                    return
                
                if not validate_dates(start_date, end_date):
                    st.error("End date must be on or after start date.")
                    return
                
                if not validate_time(start_time):
                    st.error("Please enter a valid start time.")
                    return
                
                # Check if all slugs are valid - use more flexible validation
                invalid_slugs = [slug for slug in slugs if not validate_slug(slug, None)]
                
                if invalid_slugs:
                    st.error(f"The following course codes are invalid: {', '.join(invalid_slugs)}")
                    return
                
                # Format meeting days as comma-separated string
                meeting_days_str = ','.join(meeting_days)
                
                # Format excluded meeting dates as comma-separated string
                excluded_dates_str = ','.join([date.strftime('%Y-%m-%d') for date in excluded_dates]) if excluded_dates else ''
                
                # Add each request to the session state
                for slug in slugs:
                    new_request = {
                        'slug': slug,
                        'meeting_days': meeting_days_str,
                        'start_date': start_date,
                        'end_date': end_date,
                        'start_time': start_time,
                        'excluded_meeting_dates': excluded_dates_str,
                        'requested_by': st.session_state.username,
                        'request_date': datetime.datetime.now().date(),
                        'status': 'Pending'
                    }
                    
                    # Add to session state
                    st.session_state.requests = pd.concat([
                        st.session_state.requests, 
                        pd.DataFrame([new_request])
                    ], ignore_index=True)
                
                # Show success message
                success_message = f"Successfully submitted {len(slugs)} class request(s)!"
                success_container.markdown(
                    f"""
                    <div class="temp-success-message">
                        {success_message}
                    </div>
                    <script>
                        setTimeout(function() {{
                            document.querySelector('.temp-success-message').classList.add('fade-out');
                        }}, 2000);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                
                # Increment the form reset counter to create a new form instance
                st.session_state.form_reset_counter += 1
                
                # Rerun the app to reset the form
                st.rerun()
    
    # Tab 2: Approve/Deny Requests (admin only) or My Requests (regular users)
    with tab2:
        if st.session_state.user_role == 'admin':
            st.header("Approve/Deny Requests")
            
            # Filter requests that are pending
            pending_requests = st.session_state.requests[st.session_state.requests['status'] == 'Pending']
            
            if pending_requests.empty:
                st.info("No pending requests to approve or deny.")
            else:
                st.write(f"You have {len(pending_requests)} pending requests.")
                
                col1, col2 = st.columns([1, 1])

                with col1:
                    approve_all_clicked = st.button("Approve All", key="approve_all_btn")

                with col2:
                    deny_all_clicked = st.button("Deny All", key="deny_all_btn")

                # Place the radio button below the Approve All button
                bulk_class_type = st.radio(
                    "Select Class Type for All Approvals",
                    ["Livestream", "Group Class"],
                    key="bulk_class_type",
                    horizontal=True,
                    help="This selection will be applied to all requests when using Approve All."
                )
                st.caption("This selection will be applied to all requests.")

                if approve_all_clicked:
                    pending_indices = pending_requests.index.tolist()
                    for idx in pending_indices:
                        st.session_state.requests.at[idx, 'status'] = 'Approved'
                        st.session_state.requests.at[idx, 'class_type'] = bulk_class_type
                    st.success(f"All {len(pending_indices)} pending requests have been approved as '{bulk_class_type}'!")
                    st.rerun()
                
                st.divider()
                
                # Display each request with approve/deny buttons
                for idx, (request_id, request_data) in enumerate(pending_requests.iterrows(), start=1):
                    with st.expander(f"Request: {idx}"):
                        # Create two columns - left for request details, right for approval options
                        col1, col2 = st.columns([3, 1])
                        
                        # Left column - Original Request Details (exactly as they were)
                        with col1:
                            # Display the original data exactly as it was
                            st.write(f"**Course Code:** {request_data.get('slug', '')}")
                            st.write(f"**Meeting Days:** {request_data.get('meeting_days', '')}")
                            st.write(f"**Date Range:** {request_data.get('start_date', '')} to {request_data.get('end_date', '')}")
                            st.write(f"**Start Time:** {request_data.get('start_time', '')}")
                            st.write(f"**Requested By:** {request_data.get('requested_by', '')}")
                            st.write(f"**Request Date:** {request_data.get('request_date', '')}")
                        
                        # Right column - Approval Options
                        with col2:
                            st.subheader("Approval Options")
                            
                            # Add radio buttons for class type selection
                            class_type = st.radio(
                                "Select Class Type:",
                                ["Livestream", "Group Class"],
                                key=f"class_type_{request_id}"
                            )
                            
                            # Add approve button - now directly updates the status
                            if st.button("Approve", key=f"approve_{request_id}", use_container_width=True):
                                # Update the request status to Approved
                                st.session_state.requests.at[request_id, 'status'] = 'Approved'
                                # Store the class type
                                st.session_state.requests.at[request_id, 'class_type'] = class_type
                                st.success("Request approved successfully!")
                                st.rerun()
                            
                            # Add deny button - now directly updates the status
                            if st.button("Deny", key=f"deny_{request_id}", use_container_width=True):
                                # Update the request status to Denied
                                st.session_state.requests.at[request_id, 'status'] = 'Denied'
                                st.error("Request denied.")
                                st.rerun()
        else:
            st.header("My Requests")
            
            # Filter requests for the current user
            user_requests = st.session_state.requests[st.session_state.requests['requested_by'] == st.session_state.username]
            
            if user_requests.empty:
                st.info("You haven't made any requests yet.")
            else:
                st.write(f"You have {len(user_requests)} requests.")
                
                # Display each request with status
                for _, request in user_requests.iterrows():
                    with st.container():
                        st.write(f"**Course Code:** {request['slug']}")
                        st.write(f"**Meeting Days:** {request['meeting_days']}")
                        st.write(f"**Date Range:** {request['start_date']} to {request['end_date']}")
                        st.write(f"**Start Time:** {request['start_time']}")
                        st.write(f"**Request Date:** {request['request_date']}")
                        
                        # Display status with appropriate color
                        status = request['status']
                        if status == 'Approved':
                            st.success(f"Status: {status}")
                        elif status == 'Denied':
                            st.error(f"Status: {status}")
                        else:
                            st.info(f"Status: {status}")
                        
                        st.divider()
    
    # Tab 3: Export Data (admin only)
    if st.session_state.user_role == 'admin':
        with tab3:
            st.header("Export Data")
            
            # Get approved requests
            approved_requests = st.session_state.requests[st.session_state.requests['status'] == 'Approved']
            
            if approved_requests.empty:
                st.info("No approved requests to export.")
            else:
                st.write(f"You have {len(approved_requests)} approved requests ready for export.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Process and Export"):
                        # Process the approved requests
                        processed_data = process_class_data(approved_requests)
                        
                        # Export to CSV
                        export_path = export_to_csv(processed_data, CONFIG['paths']['export_dir'])
                        
                        # Show success message
                        st.success(f"Data exported successfully to {export_path}")
                        
                        # Store the export path in session state for download
                        st.session_state.export_path = export_path
                        
                        # Provide download link
                        with open(export_path, 'rb') as f:
                            st.download_button(
                                label="Download CSV",
                                data=f,
                                file_name=os.path.basename(export_path),
                                mime="text/csv",
                                key="download_csv"
                            )
                
                with col2:
                    if st.button("Clear Approved Requests"):
                        # Remove approved requests from session state
                        st.session_state.requests = st.session_state.requests[
                            st.session_state.requests['status'] != 'Approved'
                        ].reset_index(drop=True)
                        
                        # Show success message
                        st.success("Approved requests have been cleared from the list.")
                        st.rerun()
    
    # Tab 4: Manage Courses (admin only)
    if st.session_state.user_role == 'admin':
        with tab4:
            st.markdown("<h2 style='color: green;'>Manage Courses</h2>", unsafe_allow_html=True)
            
            # Load course master data
            course_master = load_course_master_data()
            
            # Create tabs for adding/editing courses
            course_action = st.radio("Select Action", ["Add New Course", "Edit Existing Course"])
            
            if course_action == "Add New Course":
                with st.form("add_course_form"):
                    st.subheader("Add New Course")
                    
                    # Course code
                    slug = st.text_input("Course Code", help=f"Example: {CONFIG['slug_format']['example']}")
                    
                    # Course details
                    col1, col2 = st.columns(2)
                    with col1:
                        subject_name = st.text_input("Subject Name", help="E.g., Mathematics, Science, English")
                        subject_id = st.text_input("Subject ID", help="E.g., MATH, SCI, ENG")
                        grades = st.text_input("Grades", help="E.g., K-2, 3-5, 6-8, 9-12")
                    
                    with col2:
                        course_title = st.text_input("Course Title", help="E.g., Algebra Fundamentals")
                        business_units = st.text_input("Business Units", help="E.g., Varsity Tutors Platform")
                        price_dollars = st.text_input("Price ($)", value="0")
                    
                    # Content details
                    content_title = st.text_input("Content Title", help="Title for the course content")
                    content_description = st.text_area("Content Description", help="Description for the course content")
                    content_keywords = st.text_input("Content Keywords", help="Comma-separated keywords")
                    
                    # Image file
                    image_file_name = st.text_input("Image File Name", help="Name of the image file (if any)")
                    
                    submitted = st.form_submit_button("Add Course")
                    
                    if submitted:
                        # Validate inputs
                        if not validate_slug(slug, None):
                            st.error("Invalid course code format.")
                            return
                        
                        if not subject_name or not course_title:
                            st.error("Subject name and course title are required.")
                            return
                        
                        # Check if course already exists
                        if slug in course_master:
                            st.error(f"Course with code '{slug}' already exists.")
                            return
                        
                        # Add to course master
                        course_master[slug] = {
                            'subject_name': subject_name,
                            'subject_id': subject_id,
                            'grades': grades,
                            'course_title': course_title,
                            'business_units': business_units,
                            'price_dollars': price_dollars,
                            'content_title': content_title,
                            'content_description': content_description,
                            'content_keywords': content_keywords,
                            'image_file_name': image_file_name
                        }
                        
                        # Save to file
                        if save_course_master_data(course_master):
                            st.success(f"Course '{slug}' added successfully!")
                        else:
                            st.error("Error saving course data. Please try again.")
            
            else:  # Edit Existing Course
                st.session_state.action = 'edit'
                
                # Course selection dropdown
                course_options = get_course_options()
                
                if not course_options:
                    st.warning("No courses found in course_master.json")
                else:
                    # Use a selectbox for course selection
                    selected_course = st.selectbox("Select Course to Edit", course_options)
                    
                    # Automatically load course data when a course is selected
                    if selected_course:
                        course_data = load_course_data(selected_course)
                        
                        if course_data:
                            # Display form with pre-populated values
                            with st.form(key='edit_course_form'):
                                st.subheader("Edit Course Details", anchor=False)
                                
                                # Create form fields with pre-populated values and correct labels
                                # These labels match exactly what's in course_master.json
                                course_code = st.text_input("State (field_1)", value=course_data.get('field_1', ''))
                                parent = st.text_input("Parent (field_2)", value=course_data.get('field_2', ''))
                                parent_title = st.text_input("Parent Title (field_3)", value=course_data.get('field_3', ''))
                                item_name = st.text_input("Item Name (field_4)", value=course_data.get('field_4', ''))
                                commodity = st.text_input("Commodity (field_5)", value=course_data.get('field_5', ''))
                                item_type = st.text_input("Item Type (field_6)", value=course_data.get('field_6', ''))
                                business_units = st.text_input("Business Units (field_7)", value=course_data.get('field_7', ''))
                                subject_name = st.text_input("Subject Name - General (field_8)", value=course_data.get('field_8', ''))
                                subject_id = st.text_input("Subject ID (field_9)", value=course_data.get('field_9', ''))
                                
                                # For list fields, join with commas
                                grade_tags = course_data.get('field_10', [])
                                if isinstance(grade_tags, list):
                                    grade_tags = ', '.join(grade_tags)
                                parent_grade_tags = st.text_input("Parent Grade Tags (field_10)", value=grade_tags)
                                
                                days_of_week = st.text_area("Days of Week (field_11)", value=course_data.get('field_11', ''))
                                parent_course_hours = st.text_input("Parent Course Hours (field_12)", value=course_data.get('field_12', ''))
                                session_count = st.text_input("Session Count (field_13)", value=course_data.get('field_13', ''))
                                capacity = st.text_input("Capacity (field_14)", value=course_data.get('field_14', ''))
                                price = st.text_input("Price in Dollars (field_15)", value=course_data.get('field_15', ''))
                                image_link = st.text_input("Content Product Image Link (field_16)", value=course_data.get('field_16', ''))
                                
                                # For list fields, join with commas
                                item_tags = course_data.get('field_17', [])
                                if isinstance(item_tags, list):
                                    item_tags = ', '.join(item_tags)
                                item_tags_input = st.text_input("Item Tags (field_17)", value=item_tags)
                                
                                # Submit button for the form
                                submit_button = st.form_submit_button(label="Save Changes")
                                
                                if submit_button:
                                    # Update course data with form values
                                    updated_data = {
                                        'field_1': course_code,
                                        'field_2': parent,
                                        'field_3': parent_title,
                                        'field_4': item_name,
                                        'field_5': commodity,
                                        'field_6': item_type,
                                        'field_7': business_units,
                                        'field_8': subject_name,
                                        'field_9': subject_id,
                                        'field_10': [tag.strip() for tag in parent_grade_tags.split(',') if tag.strip()],
                                        'field_11': days_of_week,
                                        'field_12': parent_course_hours,
                                        'field_13': session_count,
                                        'field_14': capacity,
                                        'field_15': price,
                                        'field_16': image_link,
                                        'field_17': [tag.strip() for tag in item_tags_input.split(',') if tag.strip()]
                                    }
                                    
                                    # Save updated data to course_master.json
                                    try:
                                        file_path = os.path.join('data', 'course_master.json')
                                        with open(file_path, 'r') as f:
                                            course_master = json.load(f)
                                        
                                        course_master[selected_course] = updated_data
                                        
                                        with open(file_path, 'w') as f:
                                            json.dump(course_master, f, indent=2)
                                        
                                        st.success(f"Changes saved for {selected_course}")
                                    except Exception as e:
                                        st.error(f"Error saving changes: {str(e)}")

def load_course_data(course_slug):
    """Load course data from course_master.json for the selected course."""
    try:
        # Load course_master.json
        file_path = os.path.join('data', 'course_master.json')
        with open(file_path, 'r') as f:
            course_master = json.load(f)
        
        # Check if course exists
        if course_slug not in course_master:
            st.error(f"Course {course_slug} not found in course_master.json")
            return None
        
        # Get course data
        course_data = course_master[course_slug]
        
        # Debug output
        st.write(f"Loaded data for course: {course_slug}")
        
        return course_data
    except Exception as e:
        st.error(f"Error loading course data: {str(e)}")
        return None

def get_course_options():
    try:
        file_path = os.path.join('data', 'course_master.json')
        with open(file_path, 'r') as f:
            course_master = json.load(f)
        return list(course_master.keys())
    except Exception as e:
        st.error(f"Error loading course options: {str(e)}")
        return []

def approve_request(request_id, request_data):
    """Approve a course request by adding it to course_master.json."""
    try:
        # Debug print to see what's in request_data
        print(f"Request data received: {request_data}")
        
        # Load course_master.json
        course_master_path = os.path.join('data', 'course_master.json')
        with open(course_master_path, 'r') as f:
            course_master = json.load(f)
        
        # Extract course slug from request data
        course_slug = request_data['slug']  # Direct access since we know it exists
        
        # Check if course already exists
        if course_slug in course_master:
            st.warning(f"Course {course_slug} already exists in course_master.json.")
            return False
        
        # Get the selected class type from the radio button
        class_type = request_data.get('class_type', 'Group Class')  # Default to Group Class if not specified
        
        # Add course to course_master.json
        course_master[course_slug] = {
            'field_1': course_slug,  # Use the slug as field_1
            'field_2': request_data.get('meeting_days', ''),
            'field_3': str(request_data.get('start_date', '')),
            'field_4': str(request_data.get('end_date', '')),
            'field_5': str(request_data.get('start_time', '')),
            'field_6': request_data.get('requested_by', ''),
            'field_7': str(request_data.get('request_date', '')),
            'class_type': class_type
        }
        
        # Save updated course_master.json
        with open(course_master_path, 'w') as f:
            json.dump(course_master, f, indent=2)
        
        return True
        
    except Exception as e:
        st.error(f"Error approving request: {str(e)}")
        print(f"Error details: {str(e)}")  # Debug print
        return False

if __name__ == "__main__":
    main() 