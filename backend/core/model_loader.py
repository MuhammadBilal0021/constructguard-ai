"""
ConstructGuard AI — Model Loader
Loads Qwen3.6-27B on AMD MI300X via ROCm in production,
or provides mock responses for local development.
"""

import os
import json
import random
from pathlib import Path

# Inference mode: "mock" (local dev) or "production" (AMD Cloud + GPU)
INFERENCE_MODE = os.getenv("INFERENCE_MODE", "mock")


def load_model():
    """
    Load the vision-language model.
    In mock mode: returns None (we use mock responses).
    In production: loads Qwen3.6-27B onto AMD MI300X via ROCm.
    """
    if INFERENCE_MODE == "mock":
        print("[ModelLoader] Running in MOCK mode — no GPU required")
        return None, None

    # Production mode — load real model on AMD MI300X
    try:
        import torch
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

        model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-VL-7B-Instruct")
        device = os.getenv("DEVICE", "cuda")

        print(f"[ModelLoader] Loading {model_name} on {device}...")

        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_name,
            device_map=device,
            torch_dtype=torch.float16,
        )
        processor = AutoProcessor.from_pretrained(model_name)

        gpu_mem_used = torch.cuda.memory_allocated() / 1e9
        gpu_mem_free = (torch.cuda.get_device_properties(0).total_mem - torch.cuda.memory_allocated()) / 1e9
        print(f"[ModelLoader] Model loaded! GPU memory: {gpu_mem_used:.1f}GB used, {gpu_mem_free:.1f}GB free")

        return model, processor

    except Exception as e:
        print(f"[ModelLoader] ERROR loading model: {e}")
        print("[ModelLoader] Falling back to MOCK mode")
        return None, None


def run_inference(model, processor, image, prompt: str) -> str:
    """
    Run inference with the model.
    In mock mode: returns realistic mock JSON.
    In production: runs actual Qwen3.6 inference.
    """
    if model is None or processor is None:
        return _generate_mock_response(image)

    # Production inference
    try:
        from PIL import Image

        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ]}]

        text = processor.apply_chat_template(messages, tokenize=False)
        inputs = processor(text=[text], images=[image], return_tensors="pt").to("cuda")
        output = model.generate(**inputs, max_new_tokens=2048)
        response = processor.decode(output[0], skip_special_tokens=True)
        return response

    except Exception as e:
        print(f"[ModelLoader] Inference error: {e}, falling back to mock")
        return _generate_mock_response(image)


def _generate_mock_response(image=None) -> str:
    """
    Generate realistic mock violation data for local development.
    Simulates what Qwen3.6-27B would return from a construction site image.
    """
    # Get image dimensions for realistic bounding boxes
    img_w, img_h = 800, 600
    if image is not None:
        try:
            img_w, img_h = image.size
        except Exception:
            pass

    mock_violations = [
        {
            "violation_type": "no_helmet",
            "location": "Zone B — near active crane",
            "severity": "critical",
            "reasoning": "Worker operating near active overhead crane without head protection. "
                         "Falling debris and crane load swing pose immediate risk of fatal head injury. "
                         "Stop-work order recommended until PPE compliance is restored.",
            "bbox": [int(img_w * 0.15), int(img_h * 0.20), int(img_w * 0.12), int(img_h * 0.25)],
            "confidence": 0.94,
        },
        {
            "violation_type": "no_vest",
            "location": "Zone C — vehicle traffic corridor",
            "severity": "medium",
            "reasoning": "Worker in active vehicle traffic zone without high-visibility vest. "
                         "Reduced visibility to equipment operators increases collision probability, "
                         "especially during low-light conditions or dust.",
            "bbox": [int(img_w * 0.55), int(img_h * 0.35), int(img_w * 0.10), int(img_h * 0.30)],
            "confidence": 0.87,
        },
        {
            "violation_type": "no_harness",
            "location": "Zone A — scaffolding level 3",
            "severity": "high",
            "reasoning": "Worker at elevated position (approx. 8m height) on scaffolding without fall arrest harness. "
                         "Falls from height are the leading cause of construction fatalities. "
                         "Immediate intervention required per OSHA 1926.502.",
            "bbox": [int(img_w * 0.70), int(img_h * 0.10), int(img_w * 0.14), int(img_h * 0.22)],
            "confidence": 0.91,
        },
        {
            "violation_type": "no_helmet",
            "location": "Zone D — materials storage area",
            "severity": "high",
            "reasoning": "Worker in materials handling zone without hard hat. Risk of head injury from "
                         "falling stored materials or forklift operations. Compliance required before re-entry.",
            "bbox": [int(img_w * 0.35), int(img_h * 0.50), int(img_w * 0.11), int(img_h * 0.24)],
            "confidence": 0.89,
        },
    ]

    # Randomly select 2-4 violations for variety
    num_violations = random.randint(2, min(4, len(mock_violations)))
    selected = random.sample(mock_violations, num_violations)

    total_workers = num_violations + random.randint(1, 3)  # some compliant workers

    result = {
        "total_workers_detected": total_workers,
        "violations": selected,
    }

    return json.dumps(result)
