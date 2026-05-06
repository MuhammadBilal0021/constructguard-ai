"""
ConstructGuard AI — Reasoning Agent
Generates natural language explanations of WHY each violation is dangerous.
"""

import json
from backend.core.model_loader import run_inference

REASONING_PROMPT = """You are an OSHA construction safety expert.
Violation: {violation_type} at {location} (Severity: {severity}).
Current context: {current_reasoning}

Provide a 2-3 sentence professional analysis covering:
1. Immediate danger and injury risk
2. Relevant OSHA standard
3. Recommended corrective action

Return ONLY the reasoning text."""


class ReasoningAgent:
    """Enhances violations with detailed natural language reasoning."""

    def __init__(self, model=None, processor=None):
        self.model = model
        self.processor = processor

    def enhance_violations(self, violations: list) -> list:
        enhanced = []
        for v in violations:
            ev = dict(v)
            if self.model is not None:
                try:
                    prompt = REASONING_PROMPT.format(
                        violation_type=v.get("violation_type", "unknown"),
                        location=v.get("location", "unknown"),
                        severity=v.get("severity", "medium"),
                        current_reasoning=v.get("reasoning", "none"),
                    )
                    ev["reasoning"] = run_inference(self.model, self.processor, None, prompt).strip()
                except Exception as e:
                    print(f"[ReasoningAgent] Error: {e}")

            if not ev.get("reasoning"):
                ev["reasoning"] = self._fallback(v)
            enhanced.append(ev)
        return enhanced

    def _fallback(self, v: dict) -> str:
        vtype = v.get("violation_type", "unknown")
        loc = v.get("location", "the site")
        fallbacks = {
            "no_helmet": f"Worker at {loc} without hard hat. Head injuries from falling objects are a leading cause of construction fatalities. Immediate PPE compliance required per OSHA 1926.100.",
            "no_vest": f"Worker at {loc} missing high-visibility vest. Reduced visibility to equipment operators increases collision risk. Required per OSHA 1926.201.",
            "no_harness": f"Worker at {loc} without fall arrest harness. Falls from height are the #1 cause of construction deaths. Stop-work required per OSHA 1926.502.",
            "no_gloves": f"Worker at {loc} handling materials without protective gloves. Risk of lacerations or crush injuries. Required per OSHA 1926.95.",
            "no_goggles": f"Worker at {loc} without eye protection near hazardous operations. Risk of permanent eye damage. Required per OSHA 1926.102.",
        }
        return fallbacks.get(vtype, f"Safety violation detected at {loc}. Corrective action required.")
