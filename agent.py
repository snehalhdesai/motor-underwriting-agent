from dotenv import load_dotenv
load_dotenv()

def calculate_risk_score(age, claims, vehicle_value):
    if age < 21 or age > 70:
        age_risk = "high"
    elif age <= 29 or age >= 61:
        age_risk = "medium"
    else:
        age_risk = "low"

    if claims >= 2:
        claims_risk = "high"
    elif claims == 1:
        claims_risk = "medium"
    else:
        claims_risk = "low"

    if vehicle_value > 50000:
        value_risk = "high"
    elif vehicle_value >= 20000:
        value_risk = "medium"
    else:
        value_risk = "low"

    risks = [age_risk, claims_risk, value_risk]
    if "high" in risks:
        overall = "high"
    elif "medium" in risks:
        overall = "medium"
    else:
        overall = "low"

    return overall


def calculate_premium(risk_score, claims, vehicle_value):
    premium = 500

    if risk_score == "high":
        premium += 300
    elif risk_score == "medium":
        premium += 150

    premium += claims * 150

    if vehicle_value > 50000:
        premium += vehicle_value * 0.01

    return premium

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

from openai import OpenAI
import json

client = OpenAI()

applicant_description = "A young driver with a couple of claims wants insurance for their car."

messages = [
    {"role": "system", "content": "You are an underwriting assistant. Always calculate the risk score first using calculate_risk_score, and wait for that result before calling calculate_premium. Never guess a risk score — only use the exact result returned by calculate_risk_score."},
    {"role": "user", "content": f"Evaluate this motor insurance applicant and tell me the risk level and premium: {applicant_description}"}
]
available_functions = {
    "calculate_risk_score": calculate_risk_score,
    "calculate_premium": calculate_premium
}

# The agent loop: keep going until the model gives a final text answer
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

            print(f"Model called {function_name} with {function_args} -> result: {function_result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(function_result)
            })
        # loop again so the model can see the result and decide its next move
        continue
    else:
        # no more tool calls means the model is done
        print("\n--- Final answer ---")
        print(response_message.content)
        break