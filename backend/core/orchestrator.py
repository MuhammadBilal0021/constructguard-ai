"""
ConstructGuard AI — Orchestrator
Wires all 5 agents into a sequential pipeline:
Vision → Reasoning → Risk Scorer → Alert → Report
"""

import time
from PIL import Image

from backend.core.model_loader import load_model
from backend.core.escalation import check_escalation, store_analysis
from backend.agents.vision_agent import VisionAgent
from backend.agents.reasoning_agent import ReasoningAgent
from backend.agents.risk_scorer import RiskScorer
from backend.agents.alert_agent import AlertAgent
from backend.agents.report_agent import ReportAgent
from backend.utils.bbox_visualizer import draw_violations_on_image
from backend.utils.image_processor import get_output_path


class Orchestrator:
    """
    Central pipeline controller.
    Loads the model once and runs all 5 agents in sequence.
    """

    def __init__(self):
        print("[Orchestrator] Initializing ConstructGuard AI pipeline...")
        self.model, self.processor = load_model()
        self.vision = VisionAgent(self.model, self.processor)
        self.reasoning = ReasoningAgent(self.model, self.processor)
        self.risk_scorer = RiskScorer()
        self.alert_agent = AlertAgent()
        self.report_agent = ReportAgent()
        print("[Orchestrator] All agents initialized ✓")

    def analyze(self, image_path: str, site_id: str = "site_001") -> dict:
        """
        Run the full analysis pipeline on an image.

        Pipeline: Vision → Reasoning → Risk → Alert → BBox → Report

        Returns:
            Complete analysis result dict
        """
        start_time = time.time()
        print(f"\n[Orchestrator] ═══ Starting analysis for site: {site_id} ═══")

        # ── Agent 1: Vision ──────────────────────────
        print("[Orchestrator] [1/5] Vision Agent — detecting violations...")
        image = Image.open(image_path).convert("RGB")
        vision_result = self.vision.analyze(image)
        violations = vision_result.get("violations", [])
        total_workers = vision_result.get("total_workers_detected", 0)
        print(f"[Orchestrator]   → {len(violations)} violations, {total_workers} workers detected")

        # ── Agent 2: Reasoning ───────────────────────
        print("[Orchestrator] [2/5] Reasoning Agent — analyzing danger context...")
        violations = self.reasoning.enhance_violations(violations)
        print(f"[Orchestrator]   → Reasoning enhanced for {len(violations)} violations")

        # ── Agent 3: Risk Scorer ─────────────────────
        print("[Orchestrator] [3/5] Risk Scorer — calculating risk scores...")
        risk_result = self.risk_scorer.score(violations)
        risk_score = risk_result["overall_score"]
        violations = risk_result["scored_violations"]
        print(f"[Orchestrator]   → Risk score: {risk_score}/100 ({risk_result['risk_level']})")

        # ── Agent 4: Alert Agent ─────────────────────
        print("[Orchestrator] [4/5] Alert Agent — generating alerts...")
        alerts = self.alert_agent.generate_alerts(violations)
        print(f"[Orchestrator]   → {len(alerts)} alerts generated")

        # ── Bounding Box Visualization ───────────────
        print("[Orchestrator]       Drawing bounding boxes on image...")
        annotated_path = None
        try:
            output_path = get_output_path(image_path)
            annotated_path = draw_violations_on_image(image_path, violations, output_path)
            print(f"[Orchestrator]   → Annotated image: {annotated_path}")
        except Exception as e:
            print(f"[Orchestrator]   → BBox error: {e}")

        # ── Escalation Check ────────────────────────
        print("[Orchestrator]       Checking escalation status...")
        escalation = check_escalation(site_id, violations)
        print(f"[Orchestrator]   → Escalation: {escalation['escalation_level']}")

        # ── Agent 5: Report Agent ────────────────────
        print("[Orchestrator] [5/5] Report Agent — generating PDF report...")
        report_path = self.report_agent.generate(
            site_id=site_id,
            violations=violations,
            escalation_info=escalation,
            risk_score=risk_score,
            annotated_image_path=annotated_path,
            original_image_path=image_path,
        )
        print(f"[Orchestrator]   → Report: {report_path}")

        # ── Store in Memory ──────────────────────────
        violations_for_storage = []
        for v in violations:
            violations_for_storage.append({
                "violation_type": v.get("violation_type", ""),
                "severity": v.get("severity", ""),
                "location": v.get("location", ""),
                "reasoning": v.get("reasoning", ""),
            })
        store_analysis(site_id, violations_for_storage, risk_score, escalation["escalation_level"], report_path)

        elapsed = (time.time() - start_time) * 1000
        print(f"[Orchestrator] ═══ Analysis complete in {elapsed:.0f}ms ═══\n")

        return {
            "site_id": site_id,
            "total_workers_detected": total_workers,
            "total_violations": len(violations),
            "violations": violations,
            "alerts": alerts,
            "escalation_level": escalation["escalation_level"],
            "escalation_message": escalation["message"],
            "risk_score": risk_score,
            "annotated_image_path": annotated_path,
            "report_path": report_path,
            "processing_time_ms": round(elapsed, 1),
        }
