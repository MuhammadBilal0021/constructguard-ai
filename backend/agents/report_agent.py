"""
ConstructGuard AI — Report Agent
Coordinates PDF report generation with all analysis data.
"""

from backend.utils.pdf_generator import generate_report


class ReportAgent:
    """Generates PDF compliance reports from analysis results."""

    def generate(
        self,
        site_id: str,
        violations: list,
        escalation_info: dict,
        risk_score: float,
        annotated_image_path: str = None,
        original_image_path: str = None,
    ) -> str:
        """
        Generate a PDF compliance report.

        Returns:
            Path to the generated PDF file.
        """
        try:
            report_path = generate_report(
                site_id=site_id,
                violations=violations,
                escalation_info=escalation_info,
                risk_score=risk_score,
                annotated_image_path=annotated_image_path,
                original_image_path=original_image_path,
            )
            print(f"[ReportAgent] Report generated: {report_path}")
            return report_path
        except Exception as e:
            print(f"[ReportAgent] Error generating report: {e}")
            return None
