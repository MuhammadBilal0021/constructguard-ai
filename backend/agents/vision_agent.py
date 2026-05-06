"""
ConstructGuard AI — Vision Agent
Uses Qwen3.6-27B to analyze construction site images and detect
safety violations with bounding box coordinates.
"""

import json
from backend.core.model_loader import run_inference

# System prompt for the Vision Agent
VISION_PROMPT = """You are an expert construction site safety inspector AI.
Analyze this construction site image carefully and thoroughly.

For EACH worker visible in the image, check for:
1. Hard hat / helmet — REQUIRED in all zones
2. High-visibility safety vest — REQUIRED in vehicle/traffic zones
3. Safety harness — REQUIRED when working above 6 feet (1.8m)
4. Safety gloves — REQUIRED when handling materials
5. Safety goggles — REQUIRED near cutting/welding operations

For each safety violation you detect, provide:
- violation_type: one of [no_helmet, no_vest, no_harness, no_gloves, no_goggles, unsafe_position, zone_violation, other]
- location: descriptive location in the image (e.g., "Zone B — near crane", "left side — scaffolding level 2")
- severity: one of [critical, high, medium, low] based on immediate danger level
- reasoning: 1-2 sentence explanation of WHY this violation is dangerous given the specific context
- bbox: [x, y, width, height] approximate bounding box coordinates in pixels
- confidence: detection confidence from 0.0 to 1.0

Also report:
- total_workers_detected: total number of workers visible in the image

Return your analysis as valid JSON with this structure:
{
  "total_workers_detected": <int>,
  "violations": [
    {
      "violation_type": "<string>",
      "location": "<string>",
      "severity": "<string>",
      "reasoning": "<string>",
      "bbox": [x, y, w, h],
      "confidence": <float>
    }
  ]
}

If no violations are found, return an empty violations list.
Return ONLY the JSON, no other text."""


class VisionAgent:
    """Detects safety violations in construction site images using Qwen3.6-27B."""

    def __init__(self, model=None, processor=None):
        self.model = model
        self.processor = processor

    def analyze(self, image) -> dict:
        """
        Analyze a construction site image for safety violations.

        Args:
            image: PIL Image object

        Returns:
            Dict with total_workers_detected and violations list
        """
        raw_response = run_inference(self.model, self.processor, image, VISION_PROMPT)

        # Parse JSON from model response
        try:
            # Try to extract JSON from the response
            result = self._parse_json_response(raw_response)
            return result
        except Exception as e:
            print(f"[VisionAgent] Error parsing response: {e}")
            print(f"[VisionAgent] Raw response: {raw_response[:500]}")
            return {"total_workers_detected": 0, "violations": []}

    def _parse_json_response(self, response: str) -> dict:
        """Extract and parse JSON from model response."""
        # Try direct JSON parse first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block in response
        # Look for ```json ... ``` pattern
        if "```json" in response:
            start = response.index("```json") + 7
            end = response.index("```", start)
            return json.loads(response[start:end].strip())

        # Look for { ... } pattern
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])

        raise ValueError("No valid JSON found in response")
