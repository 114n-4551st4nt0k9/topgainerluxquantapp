import streamlit as st
import re
import pandas as pd
from datetime import datetime, timedelta
import pytz
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="Target 4 Tracker",
    page_icon="📈",
    layout="wide"
)

# ====== TIMEZONE & DEFAULT SETTINGS ======
wib = pytz.timezone("Asia/Jakarta")

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
    # Convert dates to UTC
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
        
        # Skip jika diluar range tanggal
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

        # waktu ke WIB
        date_wib = to_utc_aware(root.date).astimezone(wib)
        upd_wib  = m_utc.astimezone(wib)

        # durasi dalam menit
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
            "root_link": build_link(channel_id, root.id),
            "update_date_wib": upd_wib,
            "update_msg_id": m.id,
            "update_link": build_link(channel_id, m.id),
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
    
    # Sort berdasarkan pilihan
    if sort_by == "pct_to_t4":
        df = df.sort_values("pct_to_t4", ascending=ascending)
    elif sort_by == "duration_minutes":
        df = df.sort_values("duration_minutes", ascending=ascending)
    else:  # update_date_wib
        df = df.sort_values("update_date_wib", ascending=ascending)
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Create display dataframe
    display_df = pd.DataFrame({
        "Pair": df["pair"],
        "📋 Signal": df["root_link"],
        "Entry": df["entry"],
        "Target 4": df["target4_final"],
        "Gain %": df["pct_display"],
        "Duration": df["duration_display"],
        "Signal Time": df["date_wib"].dt.strftime('%Y-%m-%d %H:%M:%S'),
        "Hit Time": df["update_date_wib"].dt.strftime('%Y-%m-%d %H:%M:%S'),
        "✅ Hit": df["update_link"]
    })
    
    return display_df, df

# ====== MAIN APP ======
def main():
    st.title("📈 Target 4 Hit Tracker")
    st.markdown("Track trading signals that reached Target 4")
    
    # Sidebar untuk settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Get credentials from secrets
        try:
            api_id = st.secrets["api_id"]
            api_hash = st.secrets["api_hash"]
            session_string = st.secrets["session_string"]
            channel_id = int(st.secrets["channel_id"])
        except:
            st.error("Please configure secrets in Streamlit Cloud")
            st.stop()
        
        st.success("✅ Connected to Telegram")
        
        # Date range picker
        st.subheader("📅 Date Range Filter")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=7),
                max_value=datetime.now().date()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            st.stop()
        
        # Sorting options
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
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Main content area
    col1, col2, col3 = st.columns(3)
    
    # Fetch data with loading spinner
    with st.spinner("Fetching data from Telegram..."):
        try:
            # Create event loop for async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            df = loop.run_until_complete(
                scrape_only_linked_hits_wib(
                    start_date, end_date, channel_id, 
                    api_id, api_hash, session_string
                )
            )
            
            if not df.empty:
                # Format and sort dataframe
                display_df, full_df = format_dataframe(df, sort_by, ascending)
                
                # Display metrics
                with col1:
                    st.metric("Total Hits", len(df))
                
                with col2:
                    # Average gain dari top 5 performers
                    top5_avg_gain = df.nlargest(5, "pct_to_t4")["pct_to_t4"].mean()
                    st.metric("Avg Gain (Top 5)", f"{top5_avg_gain:.2f}%")
                
                with col3:
                    avg_duration = df["duration_minutes"].mean()
                    hours = int(avg_duration // 60)
                    minutes = int(avg_duration % 60)
                    st.metric("Avg Duration", f"{hours}h {minutes}m")
                
                # Display main table
                st.subheader("📊 Target 4 Hits")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistics section
                st.subheader("📈 Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top performers
                    st.markdown("**🏆 Top 5 Gainers**")
                    top_gainers = df.nlargest(5, "pct_to_t4")[["pair", "pct_display"]]
                    for idx, row in top_gainers.iterrows():
                        st.write(f"• {row['pair']}: {row['pct_display']}")
                
                with col2:
                    # Fastest hits
                    st.markdown("**⚡ Fastest 5 Hits**")
                    fastest = df.nsmallest(5, "duration_minutes")[["pair", "duration_display"]]
                    for idx, row in fastest.iterrows():
                        st.write(f"• {row['pair']}: {row['duration_display']}")
                
                # Download button - export ke Excel atau CSV
                export_df = full_df[[
                    "pair", "entry", "target4_final", "pct_display", 
                    "duration_display", "date_wib", "update_date_wib"
                ]].copy()
                export_df.columns = [
                    "Pair", "Entry", "Target 4", "Gain %", 
                    "Duration", "Signal Time", "Hit Time"
                ]
                
                # Convert datetime columns to string for Excel compatibility
                export_df["Signal Time"] = export_df["Signal Time"].dt.strftime('%Y-%m-%d %H:%M:%S')
                export_df["Hit Time"] = export_df["Hit Time"].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Try Excel first, fallback to CSV
                try:
                    from io import BytesIO
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        export_df.to_excel(writer, sheet_name='Target4_Hits', index=False)
                    excel_data = excel_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_data,
                        file_name=f"t4_hits_{start_date}_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except (ImportError, Exception) as e:
                    # Fallback to CSV if Excel export fails
                    csv_data = export_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"t4_hits_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
                    st.warning(f"Excel export failed, using CSV instead: {str(e)}")
                
            else:
                st.info("No Target 4 hits found in the selected date range.")
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Please check your credentials and try again.")

if __name__ == "__main__":
    main()
