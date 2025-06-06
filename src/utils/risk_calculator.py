# src/utils/risk_calculator.py

def calculate_risk_score(scores):
    """
    Calculate the overall risk score as the average of individual scores.
    Input: scores (list of int or float)
    Output: risk score (float)
    """
    # Filter out None or invalid scores if any
    valid_scores = [s for s in scores if isinstance(s, (int, float))]
    if not valid_scores:
        return 0
    return round(sum(valid_scores) / len(valid_scores), 2)
