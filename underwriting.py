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

def score_factor(value, low_max, medium_max):
    """
    Generic helper: given a numeric value and thresholds,
    returns points (0 = low, 5 = medium, 10 = high)
    """
    if value <= low_max:
        return 0
    elif value <= medium_max:
        return 5
    else:
        return 10


def calculate_risk_score_v2(age, claims, vehicle_value, location, vehicle_type, driving_experience, annual_mileage):
    score = 0

    if age < 21 or age > 70:
        score += 10
    elif age <= 29 or age >= 61:
        score += 5

    score += score_factor(claims, low_max=0, medium_max=1)
    score += score_factor(vehicle_value, low_max=20000, medium_max=50000)

    location_points = {"rural": 0, "suburban": 5, "urban": 10}
    score += location_points.get(location.lower(), 5)

    vehicle_type_points = {"sedan": 0, "hatchback": 0, "suv": 5, "sports": 10}
    score += vehicle_type_points.get(vehicle_type.lower(), 5)

    if driving_experience < 3:
        score += 10
    elif driving_experience < 10:
        score += 5

    score += score_factor(annual_mileage, low_max=10000, medium_max=20000)

    if score <= 15:
        risk_tier = "low"
    elif score <= 35:
        risk_tier = "medium"
    else:
        risk_tier = "high"

    return {"score": score, "risk_tier": risk_tier}

def calculate_premium_v2(score, claims, vehicle_value):
    premium = 500  # base premium

    # Scale premium loading directly with the risk score
    premium += score * 15  # each risk point adds $15

    premium += claims * 150

    if vehicle_value > 50000:
        premium += vehicle_value * 0.01

    return round(premium, 2)

# quick manual tests
print(calculate_risk_score(25, 1, 30000))
print(calculate_premium("medium", 1, 30000))
print(calculate_risk_score(45, 3, 60000))   # expect: high (3 claims, high value)
print(calculate_premium(calculate_risk_score(45, 3, 60000), 3, 60000))
print(calculate_risk_score(19, 0, 15000))   # expect: high (age <21)
print(calculate_premium(calculate_risk_score(19, 0, 15000), 0, 15000))

print(calculate_risk_score_v2(
    age=45, claims=0, vehicle_value=15000,
    location="rural", vehicle_type="sedan",
    driving_experience=20, annual_mileage=8000
))

print(calculate_risk_score_v2(
    age=19, claims=3, vehicle_value=80000,
    location="urban", vehicle_type="sports",
    driving_experience=1, annual_mileage=25000
))


print(calculate_risk_score_v2(
    age=25, claims=1, vehicle_value=30000,
    location="urban", vehicle_type="suv",
    driving_experience=4, annual_mileage=15000
))

print(calculate_premium_v2(score=40, claims=1, vehicle_value=30000))
print(calculate_premium_v2(score=0, claims=0, vehicle_value=15000))
print(calculate_premium_v2(score=70, claims=3, vehicle_value=80000))
