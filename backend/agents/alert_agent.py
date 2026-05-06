"""
ConstructGuard AI — Alert Agent
Formats structured alerts with context and recommended actions.
"""

import uuid
from datetime import datetime


# Recommended actions by violation type
RECOMMENDED_ACTIONS = {
    "no_helmet": "Issue hard hat immediately. Worker must not re-enter zone until PPE is verified.",
    "no_vest": "Provide high-visibility vest. Restrict access to vehicle traffic zones without vest.",
    "no_harness": "STOP WORK immediately. Worker must be equipped with fall arrest harness before returning to elevation.",
    "no_gloves": "Provide appropriate work gloves for material handling tasks.",
    "no_goggles": "Provide safety goggles. Halt cutting/welding operations until eye protection is worn.",
    "unsafe_position": "Relocate worker to safe position. Conduct immediate safety briefing.",
    "zone_violation": "Escort worker from restricted zone. Review site access permissions.",
}


class AlertAgent:
    """Generates structured safety alerts from scored violations."""

    def generate_alerts(self, violations: list) -> list:
        """
        Generate structured alerts from violation list.

        Args:
            violations: List of scored violation dicts

        Returns:
            List of alert dicts
        """
        alerts = []
        for v in violations:
            vtype = v.get("violation_type", "other")
            severity = v.get("severity", "medium")
            location = v.get("location", "Unknown")
            reasoning = v.get("reasoning", "")

            # Build alert message
            severity_icon = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "📋",
                "low": "ℹ️",
            }.get(severity, "📋")

            message = (
                f"{severity_icon} {severity.upper()} — "
                f"{vtype.replace('_', ' ').title()} detected at {location}. "
                f"{reasoning}"
            )

            alert = {
                "alert_id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                "violation": v,
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "recommended_action": RECOMMENDED_ACTIONS.get(vtype, "Investigate and take corrective action."),
                "severity": severity,
            }
            alerts.append(alert)

        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda a: severity_order.get(a["severity"], 4))

        return alerts
