import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# 0. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Live Group Leaderboard", page_icon="🚀", layout="wide")

# ==========================================
# 1. DATA LOADING (Live Fetching)
# ==========================================
@st.cache_data(ttl=5)
def load_data():
    """
    Simulates fetching live data from Google Sheets.
    When ready, your Google Form MUST have a question asking for their Group!
    """
    np.random.seed(int(time.time())) # Keeps the simulation completely random/live
    
    students = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", 
        "Cameron", "Quinn", "Avery", "Skyler", "Drew", "Jesse",
        "Rowan", "Charlie", "Hayden", "Peyton", "Reese", "Finley",
        "Jamie", "Kendall", "Blake", "Logan", "Parker", "Dakota"
    ]
    
    # Simulate students selecting their group (1-4) in the Google Form
    groups = [f"Group {(i % 4) + 1}" for i in range(len(students))]
    np.random.shuffle(groups) # Mix them up
    
    # Create the dataframe
    data = {
        "Student Name": students,
        "Group": groups
    }
    
    # Simulate scores (using a 1-day score for immediate live feedback, 
    # but you can easily expand this back to 7 days)
    data["Total Score"] = np.random.randint(0, 100, size=len(students))
        
    df = pd.DataFrame(data)
    
    # Simulate submissions rolling in over time
    df = df.sample(frac=np.random.uniform(0.5, 1.0)).reset_index(drop=True) 
    
    return df

# ==========================================
# 2. STREAMLIT DASHBOARD UI
# ==========================================
st.title("🚀 Live Classroom Leaderboard")
st.markdown("Groups are racing for the top spot! Submit your quizzes to push your team ahead.")
st.divider()

# Load the live data
df_raw = load_data()

# --- SUBMISSION PROGRESS BAR ---
TOTAL_CLASS_SIZE = 24 # Change this to your actual class size
current_submissions = len(df_raw)
progress_percentage = min(current_submissions / TOTAL_CLASS_SIZE, 1.0)

st.progress(progress_percentage, text=f"{current_submissions} / {TOTAL_CLASS_SIZE} quizzes submitted...")
st.write("") # small spacing

# Ensure we have data before trying to calculate winners
if not df_raw.empty:
    
    # CALCULATE GROUP AVERAGES (This drives the real-time card movement)
    # 1. Group by the 'Group' column
    # 2. Find the mean (average) score
    # 3. Sort them from highest to lowest so the winning group is always index 0
    group_stats = df_raw.groupby("Group")["Total Score"].mean().sort_values(ascending=False).reset_index()
    
    # --- TOP PERFORMERS (Group & Individual) ---
    colA, colB = st.columns(2)
    
    with colA:
        top_group = group_stats.iloc[0]
        st.success(f"🏆 **LEADING GROUP:** {top_group['Group']} (Avg: {top_group['Total Score']:.1f} pts)")
        
    with colB:
        top_student = df_raw.sort_values(by="Total Score", ascending=False).iloc[0]
        st.info(f"🌟 **TOP STUDENT:** {top_student['Student Name']} ({top_student['Total Score']} pts)")

    st.divider()

    # --- LIVE MOVING GROUP CARDS ---
    st.header("📊 Live Team Standings")
    
    # Create dynamic columns based on how many unique groups exist in the data
    cols = st.columns(len(group_stats))
    
    # Because group_stats is sorted highest-to-lowest, the cards will render 
    # in order of 1st place, 2nd place, 3rd place, etc., every 5 seconds.
    for index, row in group_stats.iterrows():
        group_name = row["Group"]
        group_avg = round(row["Total Score"], 1)
        
        # Get the individual students for this specific group
        group_df = df_raw[df_raw["Group"] == group_name].sort_values(by="Total Score", ascending=False)
        
        # Render the card in the correct position (1st, 2nd, 3rd...)
        with cols[index]:
            with st.container(border=True):
                # Use markdown to make the group name huge
                st.markdown(f"### {group_name}")
                st.metric(label="Team Average", value=group_avg)
                
                st.markdown("**Roster:**")
                roster_markdown = ""
                for _, student in group_df.iterrows():
                    roster_markdown += f"- {student['Student Name']} ({student['Total Score']} pts)\n"
                st.markdown(roster_markdown)
else:
    st.warning("Waiting for the first submission...")

# --- RAW DATA VIEW ---
with st.expander("View Backend Data"):
    if not df_raw.empty:
        st.dataframe(df_raw, use_container_width=True)

# ==========================================
# 3. AUTO-REFRESH ENGINE
# ==========================================
time.sleep(5)
st.rerun()
