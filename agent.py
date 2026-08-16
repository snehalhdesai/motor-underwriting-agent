from dotenv import load_dotenv
load_dotenv()

from underwriting import calculate_risk_score_v2, calculate_premium_v2

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

from openai import OpenAI
import json

client = OpenAI()

applicant_description = "The applicant is 25 years old, has had 1 claim in the last 5 years, drives a car worth $30,000, lives in an urban area, drives an SUV, has 4 years of driving experience, and drives about 15,000 km per year."

messages = [
    {"role": "system", "content": "You are an underwriting assistant. Always calculate the risk score first using calculate_risk_score_v2, and wait for that result before calling calculate_premium_v2. Use the exact numeric 'score' value returned — never guess or estimate it yourself."},
    {"role": "user", "content": f"Evaluate this motor insurance applicant and tell me the risk score, risk tier, and premium: {applicant_description}"}
]
available_functions = {
    "calculate_risk_score_v2": calculate_risk_score_v2,
    "calculate_premium_v2": calculate_premium_v2
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