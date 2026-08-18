import streamlit as st
from multi_agent import data_collector_agent, risk_assessor_agent, pricing_agent
import json

st.title("Motor Insurance Underwriting — Multi-Agent Version")
st.write("This version uses 3 separate agents (Data Collector → Risk Assessor → Pricing) instead of one.")

raw_description = st.text_area(
    "Describe the applicant in plain English",
    value="The applicant is 28 years old, lives in the suburbs, drives a Honda SUV, has had 1 claim, has been driving for 6 years, and does about 14000 km a year. The car is worth around $25000."
)

if st.button("Run Underwriting Pipeline"):
    with st.spinner("Step 1: Data Collector agent extracting details..."):
        structured_data = data_collector_agent(raw_description)
    st.write("**Step 1 — Structured data extracted:**")
    st.code(structured_data, language="json")

    with st.spinner("Step 2: Risk Assessor agent evaluating risk..."):
        risk_assessment = risk_assessor_agent(structured_data)
    st.write("**Step 2 — Risk assessment:**")
    st.code(risk_assessment, language="json")

    data_dict = json.loads(structured_data)
    claims = data_dict["claims"]
    vehicle_value = data_dict["vehicle_value"]

    with st.spinner("Step 3: Pricing agent calculating premium..."):
        final_result = pricing_agent(risk_assessment, claims, vehicle_value)

    st.write("**Step 3 — Final result:**")
    st.success(final_result)