import streamlit as st
import re
import pandas as pd
from datetime import datetime, timedelta
import pytz
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# ====== CUSTOM CSS - DARK GOLD THEME ======
def apply_luxquant_theme():
    st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --gold-primary: #FFD700;
        --gold-secondary: #FFC107;
        --gold-dark: #B8860B;
        --bg-black: #000000;
        --bg-dark: #0a0a0a;
        --bg-card: #1a1a1a;
        --text-white: #ffffff;
        --text-gray: #e0e0e0;
        --green: #00ff00;
        --red: #ff0000;
    }
    
    /* Global Background */
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Title Styling */
    h1 {
        color: #FFD700 !important;
        text-align: center;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        margin-bottom: 2rem;
    }
    
    h2, h3, h4 {
        color: #FFD700 !important;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFD700 !important;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetric"] label {
        color: #e0e0e0 !important;
        font-size: 0.9rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFD700 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700, #FFC107);
        color: #000000;
        font-weight: 600;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.7);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #333;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stDateInput > div > div > input:focus {
        border-color: #FFD700;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    /* Radio Buttons */
    .stRadio > label {
        color: #e0e0e0 !important;
    }
    
    /* DataFrame Styling */
    [data-testid="stDataFrame"] {
        background-color: #1a1a1a;
        border-radius: 12px;
        border: 1px solid #333;
    }
    
    .dataframe {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .dataframe th {
        background-color: #0a0a0a !important;
        color: #FFD700 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #B8860B !important;
    }
    
    .dataframe td {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border-bottom: 1px solid #333 !important;
    }
    
    .dataframe tr:hover {
        background-color: #2a2a2a !important;
    }
    
    /* Success/Error/Info Messages */
    .stSuccess {
        background-color: #1a3a1a;
        border-left: 4px solid #00ff00;
        color: #00ff00;
    }
    
    .stError {
        background-color: #3a1a1a;
        border-left: 4px solid #ff0000;
        color: #ff0000;
    }
    
    .stInfo {
        background-color: #1a1a3a;
        border-left: 4px solid #FFD700;
        color: #FFD700;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #FFD700 transparent transparent transparent !important;
    }
    
    /* Divider */
    hr {
        border-color: #333 !important;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FFD700, #FFC107);
        color: #000000;
        font-weight: 600;
        border-radius: 25px;
        border: none;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.7);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #B8860B;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="LuxQuant VIP | Top Gainer Tracker",
    page_icon="📈",
    layout="wide"
)

# Apply custom theme
apply_luxquant_theme()

# ====== TIMEZONE & DEFAULT SETTINGS ======
wib = pytz.timezone("Asia/Jakarta")
today_wib = datetime.now(wib).date()

# ====== POLA TEKS ======
pat_pair   = re.compile(r"\b([A-Z0-9]+USDT)\b")
pat_entry  = re.compile(r"\bEntry[:：]\s*([0-9]*\.?[0-9]+)", re.IGNORECASE)
pat_tgt    = re.compile(r"\bTarget\s*(\d+)\s*[:：]\s*([0-9]*\.?[0-9]+)", re.IGNORECASE)
pat_t4_hit = re.compile(r"\bTarget\s*4\s*[:：]?\s*([0-9]*\.?[0-9]+)?\b.*?(✅|hit)", re.IGNORECASE | re.DOTALL)

def parse_root(text: str):
    """Parse post utama: butuh Entry + Target4."""
    if not text:
        return None
    m_entry = pat_entry.search(text)
    tgts = {int(k): float(v) for k, v in pat_tgt.findall(text)}
    if not m_entry or 4 not in tgts:
        return None
    m_pair = pat_pair.search(text)
    return {
        "pair": m_pair.group(1) if m_pair else None,
        "entry": float(m_entry.group(1)),
        "target4": tgts[4],
    }

def is_t4_update(text: str):
    """Deteksi update 'Target 4 hit/✅' dan ambil angkanya kalau ada."""
    if not text:
        return False, None
    m = pat_t4_hit.search(text)
    return (m is not None), (float(m.group(1)) if (m and m.group(1)) else None)

def build_link(ch_id: int, msg_id: int) -> str:
    return f"https://t.me/c/{str(ch_id)[4:]}/{msg_id}"

def to_utc_aware(dt):
    return dt if dt.tzinfo else pytz.UTC.localize(dt)

async def scrape_only_linked_hits_wib(start_date, end_date, channel_id, api_id, api_hash, session_string):
    """Scrape data dengan filter tanggal yang dinamis"""
    cutoff_start_wib = wib.localize(datetime.combine(start_date, datetime.min.time()))
    cutoff_end_wib = wib.localize(datetime.combine(end_date, datetime.max.time()))
    cutoff_start_utc = cutoff_start_wib.astimezone(pytz.UTC)
    cutoff_end_utc = cutoff_end_wib.astimezone(pytz.UTC)
    
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    await client.start()
    entity = await client.get_entity(channel_id)

    rows = []

    async for m in client.iter_messages(entity):
        m_utc = to_utc_aware(m.date)
        
        if m_utc > cutoff_end_utc:
            continue
        if m_utc < cutoff_start_utc:
            break

        t4_flag, t4_val = is_t4_update(m.message or "")
        rid = getattr(m, "reply_to_msg_id", None)

        if not (t4_flag and rid):
            continue

        root = await client.get_messages(entity, ids=rid)
        root_parsed = parse_root(root.message or "")
        if not root_parsed:
            continue

        entry = root_parsed["entry"]
        target4 = t4_val if t4_val is not None else root_parsed["target4"]
        pct = (target4 - entry) / entry * 100.0

        date_wib = to_utc_aware(root.date).astimezone(wib)
        upd_wib  = m_utc.astimezone(wib)

        dur_min = (m_utc - to_utc_aware(root.date)).total_seconds() / 60.0
        dur_str = f"{int(dur_min//60)}h {int(dur_min%60)}m"

        rows.append({
            "pair": root_parsed["pair"] or "Unknown",
            "entry": entry,
            "target4_final": target4,
            "pct_to_t4": pct,
            "pct_display": f"{pct:.2f}%",
            "duration_minutes": dur_min,
            "duration_display": dur_str,
            "date_wib": date_wib,
            "root_msg_id": root.id,
            "update_date_wib": upd_wib,
            "update_msg_id": m.id,
        })

    await client.disconnect()
    
    if rows:
        df = pd.DataFrame(rows)
        return df
    else:
        return pd.DataFrame()

def format_dataframe(df, sort_by="update_date_wib", ascending=False):
    """Format dan sort dataframe"""
    if df.empty:
        return df
    
    if sort_by == "pct_to_t4":
        df = df.sort_values("pct_to_t4", ascending=ascending)
    elif sort_by == "duration_minutes":
        df = df.sort_values("duration_minutes", ascending=ascending)
    else:
        df = df.sort_values("update_date_wib", ascending=ascending)
    
    df = df.reset_index(drop=True)
    
    display_df = pd.DataFrame({
        "Pair": df["pair"],
        "Entry": df["entry"],
        "Target 4": df["target4_final"],
        "Gain %": df["pct_display"],
        "Duration": df["duration_display"],
        "Signal Time": df["date_wib"].dt.strftime('%m-%d %H:%M'),
        "Hit Time": df["update_date_wib"].dt.strftime('%m-%d %H:%M')
    })
    
    return display_df, df

# ====== MAIN APP ======
def main():
    # Header dengan styling gold
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; margin: 0;">📈 LuxQuant VIP</h1>
        <p style="color: #FFD700; font-size: 1.2rem; margin: 0.5rem 0;">
            Top Gainer Live Data - Target 4 Tracker
        </p>
        <p style="color: #e0e0e0; font-size: 0.9rem;">
            Historical Accuracy of 86.5% since 2023
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar untuk settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        try:
            api_id = st.secrets["api_id"]
            api_hash = st.secrets["api_hash"]
            session_string = st.secrets["session_string"]
            channel_id = int(st.secrets["channel_id"])
        except:
            st.error("Please configure secrets in Streamlit Cloud")
            st.stop()
        
        st.success("✅ Connected to Telegram")
        
        st.subheader("📅 Date Range Filter")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=(today_wib - timedelta(days=7)),
                max_value=today_wib
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=today_wib,
                max_value=today_wib
            )
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            st.stop()
        
        st.subheader("🔀 Sort Options")
        sort_by = st.selectbox(
            "Sort by:",
            options=[
                ("update_date_wib", "Hit Time"),
                ("pct_to_t4", "Gain Percentage"),
                ("duration_minutes", "Duration to T4")
            ],
            format_func=lambda x: x[1]
        )[0]
        
        sort_order = st.radio(
            "Order:",
            options=["Descending", "Ascending"]
        )
        ascending = sort_order == "Ascending"
        
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Period badge
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFD700, #FFC107); 
                padding: 15px; border-radius: 12px; margin-bottom: 30px; text-align: center;
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);">
        <h3 style="color: #000000; margin: 0; font-weight: 600;">
            📅 Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Fetching data from Telegram..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            df = loop.run_until_complete(
                scrape_only_linked_hits_wib(
                    start_date, end_date, channel_id, 
                    api_id, api_hash, session_string
                )
            )
            
            if not df.empty:
                display_df, full_df = format_dataframe(df, sort_by, ascending)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Hits", len(df))
                
                with col2:
                    top5_avg_gain = df.nlargest(5, "pct_to_t4")["pct_to_t4"].mean()
                    st.metric("🚀 Avg Gain (Top 5)", f"{top5_avg_gain:.2f}%")
                
                with col3:
                    avg_duration = df["duration_minutes"].mean()
                    hours = int(avg_duration // 60)
                    minutes = int(avg_duration % 60)
                    st.metric("⏰ Avg Duration", f"{hours}h {minutes}m")

                st.markdown("---")
                st.subheader("📈 Performance Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #1a1a1a, #2a2a2a); 
                                padding: 20px; border-radius: 12px; border: 1px solid #FFD700;">
                        <h4 style="color: #FFD700; margin: 0;">🏆 Top 5 Gainers</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    top_gainers = df.nlargest(5, "pct_to_t4")[["pair", "pct_display"]]
                    for idx, row in top_gainers.iterrows():
                        st.markdown(f"""
                        <div style="background: #1a1a1a; padding: 12px; border-radius: 8px; margin: 10px 0; 
                                    border-left: 4px solid #00ff00;">
                            <strong style="color: #FFD700;">{row['pair']}</strong>: 
                            <span style="color: #00ff00; font-weight: bold;">{row['pct_display']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #1a1a1a, #2a2a2a); 
                                padding: 20px; border-radius: 12px; border: 1px solid #FFD700;">
                        <h4 style="color: #FFD700; margin: 0;">⚡ Fastest 5 Hits</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    fastest = df.nsmallest(5, "duration_minutes")[["pair", "duration_display"]]
                    for idx, row in fastest.iterrows():
                        st.markdown(f"""
                        <div style="background: #1a1a1a; padding: 12px; border-radius: 8px; margin: 10px 0; 
                                    border-left: 4px solid #FFD700;">
                            <strong style="color: #FFD700;">{row['pair']}</strong>: 
                            <span style="color: #e0e0e0; font-weight: bold;">{row['duration_display']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📊 Target 4 Hits Data")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    export_df = full_df[[
                        "pair", "entry", "target4_final", "pct_display", 
                        "duration_display", "date_wib", "update_date_wib"
                    ]].copy()
                    export_df.columns = [
                        "Pair", "Entry", "Target 4", "Gain %", 
                        "Duration", "Signal Time", "Hit Time"
                    ]
                    
                    export_df["Signal Time"] = export_df["Signal Time"].dt.strftime('%Y-%m-%d %H:%M:%S')
                    export_df["Hit Time"] = export_df["Hit Time"].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    try:
                        from io import BytesIO
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                            export_df.to_excel(writer, sheet_name='Target4_Hits', index=False)
                        excel_data = excel_buffer.getvalue()
                        
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"luxquant_t4_hits_{start_date}_{end_date}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except (ImportError, Exception) as e:
                        csv_data = export_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name=f"luxquant_t4_hits_{start_date}_{end_date}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
            else:
                st.info("No Target 4 hits found in the selected date range.")
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Please check your credentials and try again.")

if __name__ == "__main__":
    main()
