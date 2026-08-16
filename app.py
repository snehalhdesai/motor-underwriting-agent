import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import json
from underwriting import calculate_risk_score_v2, calculate_premium_v2

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_risk_score_v2",
            "description": "Calculates a weighted risk score (0-70) and risk tier (low, medium, high) for a motor insurance applicant based on age, claims history, vehicle value, location, vehicle type, driving experience, and annual mileage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age": {"type": "integer", "description": "The applicant's age in years"},
                    "claims": {"type": "integer", "description": "Number of insurance claims in the last 5 years"},
                    "vehicle_value": {"type": "number", "description": "The market value of the vehicle in dollars"},
                    "location": {"type": "string", "description": "One of: rural, suburban, urban"},
                    "vehicle_type": {"type": "string", "description": "One of: sedan, hatchback, suv, sports"},
                    "driving_experience": {"type": "integer", "description": "Years of driving experience"},
                    "annual_mileage": {"type": "integer", "description": "Estimated annual mileage in km"}
                },
                "required": ["age", "claims", "vehicle_value", "location", "vehicle_type", "driving_experience", "annual_mileage"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_premium_v2",
            "description": "Calculates the insurance premium in dollars based on the applicant's numeric risk score, claims history, and vehicle value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "score": {"type": "integer", "description": "The numeric risk score (0-70) returned by calculate_risk_score_v2"},
                    "claims": {"type": "integer", "description": "Number of insurance claims in the last 5 years"},
                    "vehicle_value": {"type": "number", "description": "The market value of the vehicle in dollars"}
                },
                "required": ["score", "claims", "vehicle_value"]
            }
        }
    }
]

available_functions = {
    "calculate_risk_score_v2": calculate_risk_score_v2,
    "calculate_premium_v2": calculate_premium_v2
}

st.title("Motor Insurance Underwriting Agent")
st.write("Enter applicant details below and let the agent evaluate the risk and premium.")

age = st.number_input("Applicant age", min_value=16, max_value=100, value=30)
claims = st.number_input("Number of claims in the last 5 years", min_value=0, max_value=10, value=0)
vehicle_value = st.number_input("Vehicle value ($)", min_value=1000, max_value=500000, value=20000, step=1000)
location = st.selectbox("Location type", ["rural", "suburban", "urban"])
vehicle_type = st.selectbox("Vehicle type", ["sedan", "hatchback", "suv", "sports"])
driving_experience = st.number_input("Years of driving experience", min_value=0, max_value=80, value=5)
annual_mileage = st.number_input("Estimated annual mileage (km)", min_value=0, max_value=100000, value=12000, step=1000)

if st.button("Evaluate Applicant"):
    applicant_description = f"The applicant is {age} years old, has had {claims} claims in the last 5 years, drives a car worth ${vehicle_value}, lives in a {location} area, drives a {vehicle_type}, has {driving_experience} years of driving experience, and drives about {annual_mileage} km per year."

    messages = [
        {"role": "system", "content": "You are an underwriting assistant. Always calculate the risk score first using calculate_risk_score_v2, and wait for that result before calling calculate_premium_v2. Use the exact numeric 'score' value returned — never guess or estimate it yourself."},
        {"role": "user", "content": f"Evaluate this motor insurance applicant and tell me the risk score, risk tier, and premium: {applicant_description}"}
    ]

    with st.spinner("Agent is evaluating the applicant..."):
        while True:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )

            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    function_to_call = available_functions[function_name]
                    function_result = function_to_call(**function_args)

                    st.write(f"🔧 Agent called `{function_name}` with `{function_args}` → result: **{function_result}**")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(function_result)
                    })
                continue
            else:
                st.success(response_message.content)
                break