import streamlit as st
import radioactivedecay as rd
import numpy as np
import plotly.graph_objects as go

# Skeleton to be modified

# Simulated data for the radioisotopes
radioisotopes = {
    "Isotope A": {"x": np.linspace(0, 10, 100), "y1": np.sin(np.linspace(0, 10, 100)), "y2": np.cos(np.linspace(0, 10, 100))},
    "Isotope B": {"x": np.linspace(0, 10, 100), "y1": np.exp(np.linspace(0, 10, 100) / 10), "y2": np.log(np.linspace(1, 10, 100))},
    "Isotope C": {"x": np.linspace(0, 10, 100), "y1": np.tan(np.linspace(0, 10, 100) / 2), "y2": np.sqrt(np.linspace(0, 10, 100))}
}

# Streamlit layout
st.title("Radioisotope Data Visualization")

# 1. Dropdown to select radioisotope
radioisotope = st.selectbox("Select a Radioisotope:", options=list(radioisotopes.keys()))

# Get the selected isotope's data
data = radioisotopes[radioisotope]

# 2. Plotting the graph with two lines
fig = go.Figure()

# Add the first line (y1)
fig.add_trace(go.Scatter(x=data['x'], y=data['y1'], mode='lines', name='Line 1'))

# Add the second line (y2)
fig.add_trace(go.Scatter(x=data['x'], y=data['y2'], mode='lines', name='Line 2'))

# 3. Mouseover to see the proportions of each line
fig.update_layout(
    title=f"Graph for {radioisotope}",
    xaxis_title="X",
    yaxis_title="Y",
    hovermode="closest"  # Display the closest point when you hover over the graph
)

# Display the plot
st.plotly_chart(fig)

# 4. Input box for a specific x value
x_value = st.number_input("Enter an x value:", min_value=0.0, max_value=10.0, step=0.1)

# Get the corresponding y values for both lines at the given x value
y1_value = np.interp(x_value, data['x'], data['y1'])
y2_value = np.interp(x_value, data['x'], data['y2'])

# Display the y values at the selected x value
st.write(f"For x = {x_value},")
st.write(f"  - Line 1 (y1) = {y1_value:.2f}")
st.write(f"  - Line 2 (y2) = {y2_value:.2f}")