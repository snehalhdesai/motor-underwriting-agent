from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import json
from underwriting import calculate_risk_score_v2, calculate_premium_v2

client = OpenAI()


def run_agent(system_prompt, user_message, tools, available_functions):
    """
    A reusable agent loop — same pattern as your original agent,
    but generic so any agent can use it with its own prompt and tools.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools if tools else None
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_to_call = available_functions[function_name]
                function_result = function_to_call(**function_args)

                print(f"  [{function_name}] called with {function_args} -> {function_result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(function_result)
                })
            continue
        else:
            return response_message.content


# ─────────────────────────────────────────────
# AGENT 1: DATA COLLECTOR
# ─────────────────────────────────────────────

def data_collector_agent(raw_description):
    system_prompt = (
        "You extract structured applicant data from free text descriptions. "
        "Always respond with ONLY a valid JSON object (no other text) containing exactly these keys: "
        "age (integer), claims (integer), vehicle_value (number), location (one of: rural, suburban, urban), "
        "vehicle_type (one of: sedan, hatchback, suv, sports), driving_experience (integer years), "
        "annual_mileage (integer km). If any value is missing from the description, make a reasonable estimate "
        "and note it, but always return complete JSON."
    )

    result = run_agent(system_prompt, raw_description, tools=None, available_functions=None)
    return result


# quick test
if __name__ == "__main__":
    raw_input_text = "The applicant is 28 years old, lives in the suburbs, drives a Honda SUV, has had 1 claim, has been driving for 6 years, and does about 14000 km a year. The car is worth around $25000."

    print("Running Data Collector agent...")
    output = data_collector_agent(raw_input_text)
    print("\nRaw output from agent:")
    print(output)


    # ─────────────────────────────────────────────
# AGENT 2: RISK ASSESSOR
# ─────────────────────────────────────────────

risk_tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_risk_score_v2",
            "description": "Calculates a weighted risk score (0-70) and risk tier (low, medium, high) for a motor insurance applicant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age": {"type": "integer"},
                    "claims": {"type": "integer"},
                    "vehicle_value": {"type": "number"},
                    "location": {"type": "string"},
                    "vehicle_type": {"type": "string"},
                    "driving_experience": {"type": "integer"},
                    "annual_mileage": {"type": "integer"}
                },
                "required": ["age", "claims", "vehicle_value", "location", "vehicle_type", "driving_experience", "annual_mileage"]
            }
        }
    }
]

risk_functions = {
    "calculate_risk_score_v2": calculate_risk_score_v2
}


def risk_assessor_agent(structured_data_json):
    system_prompt = (
        "You are a risk assessment agent. You receive structured applicant data as JSON. "
        "Call calculate_risk_score_v2 with the exact values provided. "
        "Then respond with ONLY a JSON object containing: score (integer), risk_tier (string), "
        "and needs_human_review (boolean, true if risk_tier is 'high', otherwise false)."
    )

    result = run_agent(system_prompt, structured_data_json, risk_tools, risk_functions)
    return result


# quick test - update the bottom of the file
if __name__ == "__main__":
    raw_input_text = "The applicant is 28 years old, lives in the suburbs, drives a Honda SUV, has had 1 claim, has been driving for 6 years, and does about 14000 km a year. The car is worth around $25000."

    print("Running Data Collector agent...")
    collected_data = data_collector_agent(raw_input_text)
    print("\nStructured data:")
    print(collected_data)

    print("\nRunning Risk Assessor agent...")
    risk_result = risk_assessor_agent(collected_data)
    print("\nRisk assessment:")
    print(risk_result)


    # ─────────────────────────────────────────────
# AGENT 3: PRICING AGENT
# ─────────────────────────────────────────────

pricing_tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_premium_v2",
            "description": "Calculates the insurance premium in dollars based on the applicant's numeric risk score, claims history, and vehicle value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "score": {"type": "integer"},
                    "claims": {"type": "integer"},
                    "vehicle_value": {"type": "number"}
                },
                "required": ["score", "claims", "vehicle_value"]
            }
        }
    }
]

pricing_functions = {
    "calculate_premium_v2": calculate_premium_v2
}


def pricing_agent(risk_assessment_json, claims, vehicle_value):
    system_prompt = (
        "You are a pricing agent. You receive a risk assessment as JSON, plus claims count and vehicle value. "
        "Call calculate_premium_v2 using the 'score' from the risk assessment, along with claims and vehicle_value. "
        "Then write a short, friendly final summary for the customer including: the risk tier, the premium amount, "
        "and one sentence on what drove the price. If needs_human_review is true, mention this will be reviewed "
        "by a human underwriter before final approval."
    )

    user_message = f"Risk assessment: {risk_assessment_json}\nClaims: {claims}\nVehicle value: {vehicle_value}"
    result = run_agent(system_prompt, user_message, pricing_tools, pricing_functions)
    return result

# ─────────────────────────────────────────────
# CONTROLLER
# ─────────────────────────────────────────────

def run_underwriting_pipeline(raw_description):
    print("Step 1: Data Collector agent running...")
    structured_data = data_collector_agent(raw_description)
    print(f"  -> {structured_data}\n")

    print("Step 2: Risk Assessor agent running...")
    risk_assessment = risk_assessor_agent(structured_data)
    print(f"  -> {risk_assessment}\n")

    # Extract claims and vehicle_value from the structured data to pass along
    data_dict = json.loads(structured_data)
    claims = data_dict["claims"]
    vehicle_value = data_dict["vehicle_value"]

    print("Step 3: Pricing agent running...")
    final_result = pricing_agent(risk_assessment, claims, vehicle_value)
    print(f"  -> {final_result}\n")

    return final_result


if __name__ == "__main__":
    raw_input_text = "The applicant is 28 years old, lives in the suburbs, drives a Honda SUV, has had 1 claim, has been driving for 6 years, and does about 14000 km a year. The car is worth around $25000."

    print("=" * 50)
    print("RUNNING FULL 3-AGENT UNDERWRITING PIPELINE")
    print("=" * 50)

    final_output = run_underwriting_pipeline(raw_input_text)

    print("=" * 50)
    print("FINAL RESULT:")
    print(final_output)