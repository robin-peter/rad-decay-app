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


def parse_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        st.error("Invalid time format. Please enter time as HH:MM.")
        return None
    
def parse_nuclide(chain_str):
    return chain_str.split(" / ")

# Title and information
st.title("Radioactive Decay and Ingrowth")
st.markdown("""
    This is a simple program to display and calculate the ingrowth of progeny in radioactive samples. The app uses radioactive decay data from the radioactive decay Python package (https://pypi.org/project/radioactivedecay/), based on ICRP Publication 107. *Currently, only Th-227 / Ra-223 and Ac-225 / Bi-213 are implemented.*

    ### Instructions:
    1. Select the decay series from the dropdown menu.
    2. Fill in the initial inventory amount of each isotope. This could be a measurement or, e.g., the vendor-provided values. Also provide the date and time of this measurement. (These values are not required if you only want to look at relative decay.)
    3. Hover over the figure to see the decay and ingrowth of the isotopes over time.
    4. Activity at specific time points can be calculated below. You can select a date/time combination or manually input a decay time.
        * The units correspond to the Figure time units, which you can change in the drop-down menus.

    For suggestions or assistance, please contact me (https://github.com/robin-peter/rad-decay-app).
""")

# Dropdown
radioisotopes = ["Th-227 / Ra-223",
                 "Ac-225 / Bi-213"]
# more can be added in future versions
radioisotope = st.selectbox("Select a Radioisotope:", options=list(radioisotopes))
a_units = ["uCi", "mCi", "Ci", "Bq", "kBq", "MBq"]
t_units = ["d", "h", "m", "s"]
t_factors = [(3600 * 24), 3600, 60, 1] # factor by which to convert s to the time unit above

nuc_p, nuc_d = parse_nuclide(radioisotope)

# User input initial conditions
col1, col2, col3 = st.columns(3)

with col1:
    Aa0 = st.number_input(f"Initial {nuc_p} activity:", min_value=0.0, max_value=200.0, value=1.0, step=0.1, format="%.3f")
    selected_date = st.date_input("Date/time of initial activity:", datetime.date.today())
    
with col2:
    Ab0 = st.number_input(f"Initial {nuc_d} activity:", min_value=0.0, max_value=200.0, value=0.0, step=0.1, format="%.3f")
    time_input = st.text_input("(HH:MM, 24-hour time)", "12:00")

with col3:
    A_unit = st.selectbox("Activity Units", options=a_units)
    t_unit = st.selectbox("Figure Time Units", options=t_units)
    t_factor = t_factors[t_units.index(t_unit)]

t = parse_time(time_input)
t0 = datetime.datetime.combine(selected_date, t)

# Get the selected isotope's data
thalf_p = rd.Nuclide(nuc_p).half_life() / t_factor
thalf_d = rd.Nuclide(nuc_d).half_life() / t_factor

max_value = 12*thalf_d

# Use radioactive decay package (which uses Bateman eqns)
inv = rd.Inventory({nuc_p: Aa0 , nuc_d: Ab0 }, units=A_unit)
df = inv.decay_time_series_pandas(time_period=max_value, time_units=t_unit, decay_units=A_unit)
df = df[[nuc_p, nuc_d]] # select only relevant isotopes (from among whole chain)

# Plot figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df[nuc_p], mode='lines', name=nuc_p))
fig.add_trace(go.Scatter(x=df.index, y=df[nuc_d], mode='lines', name=nuc_d))

# Mouseover values
fig.update_layout(
    title=f"{radioisotope} Growth and Decay",
    xaxis_title=f"Time ({t_unit})",
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

x = st.number_input(f"Or specify time point manually ({t_unit}):", min_value=0.0, max_value=max_value, step=0.1, value=dt)

y1 = np.interp(x, df.index, df[nuc_p])
y2 = np.interp(x, df.index, df[nuc_d])

y1_pct = round(y1 / (y1+y2) * 100, 1)
y2_pct = round(y2 / (y1+y2) * 100, 1)

# Display the y values at the selected x value
st.write(f"Activity distribution after {x} d:")
# st.write(f"  Th-227 activity : {y1 :.2f} uCi ({y1_pct :.1f}%)")
# st.write(f"  Ra-223 activity : {y2 :.2f} uCi ({y2_pct :.1f}%)")

# I like the default number formatting more so do rounding instead of in-line
y1 = round(y1, 2)
y2 = round(y2, 2)

st.write(nuc_p+":", y1, A_unit, "(", y1_pct, "%)")
st.write(nuc_d+":", y1, A_unit, "(", y2_pct, "%)")
