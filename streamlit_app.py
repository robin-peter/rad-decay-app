import streamlit as st
import radioactivedecay as rd
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import datetime

# TODO:
# - Add info about the radionuclide / other radionuclides
# - Add decay chain plot
# - Units for time
# - Toggle the x-axis between date and time

# Title and information
st.title("Radioactive Decay and Ingrowth")
st.markdown("""
    This is a simple program to display and calculate the ingrowth of progeny in radioactive samples.
    Currently, only the one-step decay between Th-227 and Ra-223 is supported.
    The app uses radioactive decay data from the radioactive decay Python package (https://pypi.org/project/radioactivedecay/), based on ICRP Publication 107.

    ### Instructions:
    1. Select the decay series from the dropdown menu.
    2. Fill in the initial inventory amount of each isotope. This could be a measurement or, e.g., the vendor-provided values. Also provide the date and time of this measurement. (These values are not required if you only want to look at relative decay.)
    3. Hover over the figure to see the decay and ingrowth of the isotopes over time.
    4. Activity at specific time points can be calculated below. You can select a date/time combination or manually input a decay time.

    For suggestions or assistance, please contact me (https://github.com/robin-peter/rad-decay-app).
""")

# Dropdown
radioisotopes = ["Th-227 / Ra-223"] # To be updated in future versions
radioisotope = st.selectbox("Select a Radioisotope:", options=list(radioisotopes))
units = ["uCi", "mCi", "Ci", "Bq", "kBq", "MBq"]

if radioisotope == "Th-227 / Ra-223":
    nuc1 = "Th-227"
    nuc2 = "Ra-223"

# User input initial conditions
col1, col2, col3 = st.columns(3)

with col1:
    Aa0 = st.number_input(f"Initial {nuc1} activity:", min_value=0.0, max_value=200.0, value=1.0, step=0.1, format="%.3f")
    selected_date = st.date_input("Date/time of initial activity:", datetime.date.today())
    
with col2:
    Ab0 = st.number_input(f"Initial {nuc2} activity:", min_value=0.0, max_value=200.0, value=0.0, step=0.1, format="%.3f")
    time_input = st.text_input("(HH:MM, 24-hour time)", "12:00")

with col3:
    A_unit = st.selectbox("Units", options=units)


def parse_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        st.error("Invalid time format. Please enter time as HH:MM.")
        return None

t = parse_time(time_input)
t0 = datetime.datetime.combine(selected_date, t)

thalf_th227 = 18.7 # d
thalf_ra223 = 11.4 # d # replace with data from the package
max_value = 12*thalf_ra223

# Get the selected isotope's data
if radioisotope == "Th-227 / Ra-223":
    # nuc = rd.Nuclide('Th-227')
    inv = rd.Inventory({'Th-227': Aa0 , 'Ra-223': Ab0 }, units=A_unit)
    df = inv.decay_time_series_pandas(time_period=max_value, time_units='d', decay_units=A_unit)
    df = df[['Ra-223', 'Th-227']]

    # Plot figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Th-227'], mode='lines', name='Th-227'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Ra-223'], mode='lines', name='Ra-223'))

# Mouseover values
fig.update_layout(
    title=f"{radioisotope} Growth and Decay",
    xaxis_title="Time (d)",
    yaxis_title=f"Activity ({A_unit})",
    hovermode="x"
)

st.plotly_chart(fig)

# Calculate specific time point
col1, col2, col3 = st.columns(3)

with col1:
    d1 = st.date_input("Enter date/time to evaluate:", datetime.date.today())
with col2:
    t = st.text_input("(HH:MM)", "12:00")

if d1 and t:
    t = parse_time(t)
    t1 = datetime.datetime.combine(d1, t)
    dt = min(np.abs(t0 - t1), np.abs(-(t0 - t1)))
    dt = dt.total_seconds() / 3600 / 24 # d
    x = dt

x = st.number_input("Or specify time point manually (d):", min_value=0.0, max_value=max_value, step=0.1, value=dt)

y1 = np.interp(x, df.index, df['Th-227'])
y2 = np.interp(x, df.index, df['Ra-223'])

y1_pct = y1 / (y1+y2) * 100
y2_pct = y2 / (y1+y2) * 100

# Display the y values at the selected x value
st.write(f"Activity distribution after {x} d:")
st.write(f"  Th-227 activity : {y1 :.2f} uCi ({y1_pct :.1f}%)")
st.write(f"  Ra-223 activity : {y2 :.2f} uCi ({y2_pct :.1f}%)")