import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import json
from underwriting import calculate_risk_score, calculate_premium

client = OpenAI()

st.title("Motor Insurance Underwriting Agent")
st.write("Enter applicant details below and let the agent evaluate the risk and premium.")

age = st.number_input("Applicant age", min_value=16, max_value=100, value=30)
claims = st.number_input("Number of claims in the last 5 years", min_value=0, max_value=10, value=0)
vehicle_value = st.number_input("Vehicle value ($)", min_value=1000, max_value=500000, value=20000, step=1000)

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_risk_score",
            "description": "Calculates the overall risk level (low, medium, or high) for a motor insurance applicant based on their age, claims history, and vehicle value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age": {"type": "integer", "description": "The applicant's age in years"},
                    "claims": {"type": "integer", "description": "Number of insurance claims in the last 5 years"},
                    "vehicle_value": {"type": "number", "description": "The market value of the vehicle in dollars"}
                },
                "required": ["age", "claims", "vehicle_value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_premium",
            "description": "Calculates the insurance premium in dollars based on the applicant's risk score, claims history, and vehicle value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_score": {"type": "string", "description": "The overall risk level: low, medium, or high"},
                    "claims": {"type": "integer", "description": "Number of insurance claims in the last 5 years"},
                    "vehicle_value": {"type": "number", "description": "The market value of the vehicle in dollars"}
                },
                "required": ["risk_score", "claims", "vehicle_value"]
            }
        }
    }
]

available_functions = {
    "calculate_risk_score": calculate_risk_score,
    "calculate_premium": calculate_premium
}

if st.button("Evaluate Applicant"):
    applicant_description = f"The applicant is {age} years old, has had {claims} claims in the last 5 years, and drives a car worth ${vehicle_value}."

    messages = [
        {"role": "system", "content": "You are an underwriting assistant. Always calculate the risk score first using calculate_risk_score, and wait for that result before calling calculate_premium. Never guess a risk score — only use the exact result returned by calculate_risk_score."},
        {"role": "user", "content": f"Evaluate this motor insurance applicant and tell me the risk level and premium: {applicant_description}"}
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