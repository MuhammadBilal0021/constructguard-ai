"""
ConstructGuard AI — Risk Scorer Agent
Assigns severity levels based on violation type, location context, and combinations.
"""


# Risk weights by violation type
VIOLATION_WEIGHTS = {
    "no_helmet": 30,
    "no_harness": 35,
    "no_vest": 15,
    "no_gloves": 10,
    "no_goggles": 12,
    "unsafe_position": 25,
    "zone_violation": 20,
    "other": 10,
}

# Severity multipliers
SEVERITY_MULTIPLIERS = {
    "critical": 2.0,
    "high": 1.5,
    "medium": 1.0,
    "low": 0.5,
}


class RiskScorer:
    """Calculates composite risk scores for construction site analysis."""

    def score(self, violations: list) -> dict:
        """
        Calculate an overall risk score (0-100) and per-violation scores.

        Args:
            violations: List of violation dicts

        Returns:
            Dict with overall_score, severity_breakdown, and scored_violations
        """
        if not violations:
            return {
                "overall_score": 0.0,
                "risk_level": "safe",
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "scored_violations": [],
            }

        total_score = 0.0
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        scored = []

        for v in violations:
            vtype = v.get("violation_type", "other")
            severity = v.get("severity", "medium").lower()
            confidence = v.get("confidence", 0.8)

            base = VIOLATION_WEIGHTS.get(vtype, 10)
            multiplier = SEVERITY_MULTIPLIERS.get(severity, 1.0)
            score = base * multiplier * confidence

            total_score += score
            if severity in breakdown:
                breakdown[severity] += 1

            sv = dict(v)
            sv["risk_points"] = round(score, 1)
            scored.append(sv)

        # Normalize to 0-100
        overall = min(100.0, total_score)

        # Determine risk level
        if overall >= 70 or breakdown["critical"] >= 2:
            risk_level = "critical"
        elif overall >= 50 or breakdown["critical"] >= 1:
            risk_level = "high"
        elif overall >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "overall_score": round(overall, 1),
            "risk_level": risk_level,
            "severity_breakdown": breakdown,
            "scored_violations": scored,
        }
