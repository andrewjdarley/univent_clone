import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from utils import getAssignments

def assign_colors(courses):
    colors = [
        '#FF4136', # Red
        '#0074D9', # Blue
        '#2ECC40', # Green
        '#FFDC00', # Yellow
        '#FF851B', # Orange
        '#B10DC9', # Purple
        '#01FF70', # Lime
        '#7FDBFF', # Aqua
        '#F012BE', # Fuchsia
        '#85144b'  # Maroon
    ]
    
    sorted_courses = sorted(set(courses))
    return {course: colors[i % len(colors)] for i, course in enumerate(sorted_courses)}

def main():
    st.set_page_config(page_title="Combined Academic Schedule", layout="wide")
    
    # CSS to center content and style the blocks
    st.markdown("""
    <style>
    .reportview-container .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
        margin: 0 auto;
    }
    .assignment-block {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Agenda")

    # Get assignments
    assignments = getAssignments()
    assignments = pd.DataFrame(assignments)

    # Assign colors to courses
    course_colors = assign_colors(assignments['COURSE'])

    # Generate dates for the next 60 days
    start_date = datetime.now().date()
    dates = [start_date + timedelta(days=i) for i in range(60)]

    # Create a DataFrame with all dates
    df = pd.DataFrame({'Date': dates})
    
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    df['Weekday'] = df['Date'].dt.strftime('%A')

    # Extract date from 'DTSTART' using string slicing
    assignments['Date'] = pd.to_datetime(assignments['DTSTART'].str[:10])

    # Merge assignments with dates
    df = df.merge(assignments, on='Date', how='left')

    # Group assignments by date
    grouped = df.groupby('Date')

    # Display the calendar
    for date, group in grouped:
        weekday = group['Weekday'].iloc[0]
        
        st.subheader(f"{weekday}, {date.strftime('%B %d, %Y')}")
        
        assignments_for_day = group[group['SUMMARY'].notna()]
        
        if not assignments_for_day.empty:
            for _, row in assignments_for_day.iterrows():
                course = row['COURSE']
                color = course_colors[course]
                st.markdown(f"""
                <div class="assignment-block" style="background-color: {color}40;">
                    <span style="color: {color};">●</span> <strong>{row['SUMMARY']}</strong> ({course})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No assignments due")
        
        st.markdown("---")

if __name__ == "__main__":
    main()