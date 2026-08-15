def calculate_risk_score(age, claims, vehicle_value):
    # Step 1: figure out age risk
    if age < 21 or age > 70:
        age_risk = "high"
    elif age <= 29 or age >= 61:
        age_risk = "medium"
    else:
        age_risk = "low"

    # Step 2: figure out claims risk
    if claims >= 2:
        claims_risk = "high"
    elif claims == 1:
        claims_risk = "medium"
    else:
        claims_risk = "low"

    # Step 3: figure out vehicle value risk
    if vehicle_value > 50000:
        value_risk = "high"
    elif vehicle_value >= 20000:
        value_risk = "medium"
    else:
        value_risk = "low"

    # Step 4: combine into one overall risk score
    risks = [age_risk, claims_risk, value_risk]
    if "high" in risks:
        overall = "high"
    elif "medium" in risks:
        overall = "medium"
    else:
        overall = "low"

    return overall


def calculate_premium(risk_score, claims, vehicle_value):
    premium = 500  # base premium

    if risk_score == "high":
        premium += 300
    elif risk_score == "medium":
        premium += 150

    premium += claims * 150

    if vehicle_value > 50000:
        premium += vehicle_value * 0.01

    return premium


# quick manual tests
print(calculate_risk_score(25, 1, 30000))
print(calculate_premium("medium", 1, 30000))
print(calculate_risk_score(45, 3, 60000))   # expect: high (3 claims, high value)
print(calculate_premium(calculate_risk_score(45, 3, 60000), 3, 60000))
print(calculate_risk_score(19, 0, 15000))   # expect: high (age <21)
print(calculate_premium(calculate_risk_score(19, 0, 15000), 0, 15000))
