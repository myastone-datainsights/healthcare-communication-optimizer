import re
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

# ============================================================
# Load HuggingFace Token
# ============================================================
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HUGGINGFACE_TOKEN")

torch.manual_seed(42)

model_id = "google/medgemma-1.5-4b-it"

print("Loading MedGemma 1.5 4B ...")

processor = AutoProcessor.from_pretrained(model_id, token=hf_token)
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    token=hf_token,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

print(f"\nModel loaded on {model.device}\n")


# ============================================================
# STAGE 1 — DETERMINISTIC CONTENT NORMALIZER
# ============================================================

def deterministic_normalize(text):
    """
    Rule-based content normalizer:
    - Extracts MEDICATION, CARE, and WARNING content
    - Removes duplicates
    - Removes filler phrases
    - Standardizes structure
    - Does NOT expand or simplify
    """

    # Basic cleanup
    text = text.replace("\n", " ").strip()

    # Sentence split
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Buckets
    meds, care, warn = [], [], []

    for s in sentences:
        s_clean = s.strip()

        # Medication heuristics
        if any(x in s_clean.lower() for x in ["mg", "tablet", "dose", "take", "medication"]):
            meds.append(s_clean)
            continue

        # Warning heuristics
        if any(x in s_clean.lower() for x in ["call", "seek", "emergency", "fever", "severe"]):
            warn.append(s_clean)
            continue

        # Everything else → care
        care.append(s_clean)

    # Deduplicate while preserving order
    def dedupe(lst):
        seen = set()
        out = []
        for item in lst:
            if item not in seen:
                out.append(item)
                seen.add(item)
        return out

    meds = dedupe(meds)
    care = dedupe(care)
    warn = dedupe(warn)

    # Build normalized structure
    normalized = (
        "**MEDICATION**\n" +
        "\n".join(f"- {m}" for m in meds) +
        "\n\n**CARE INSTRUCTIONS**\n" +
        "\n".join(f"- {c}" for c in care) +
        "\n\n**URGENT WARNING SIGNS**\n" +
        "\n".join(f"- {w}" for w in warn)
    )

    return normalized


# ============================================================
# STAGE 2 — READING LEVEL TRANSFORMER (Architecture A‑v6)
# ============================================================

TRANSFORMER_PROMPT = """
Transform the following normalized discharge instructions into clear, respectful,
adult-appropriate patient instructions at a 4.5–5.5 grade reading level.

RULES:
- Preserve all clinical meaning
- No new warnings or symptoms
- No new medications
- No reasoning or planning
- No duplication
- No condescending tone
- Use full sentences
- Keep structure exactly the same

Sections required:
**MEDICATION**
**WHAT TO DO / WHAT NOT TO DO**
**CALL DOCTOR RIGHT AWAY IF**

Normalized Input:
"""


# ============================================================
# Test Scenarios
# ============================================================

scenarios = [
    {
        "name": "Acetaminophen",
        "input": """Acetaminophen 500mg tablets. Take 1-2 tablets orally every 6 hours as needed for pain. Do not exceed 4000mg in 24 hours. Avoid alcohol while taking this medication. Contact provider if pain persists beyond 72 hours or if fever develops."""
    },
    {
        "name": "Hip Surgery",
        "input": """Post-operative total hip arthroplasty discharge protocol:
- Maintain hip precautions: avoid flexion >90°, adduction past midline, and internal rotation
- Prophylactic anticoagulation: Rivaroxaban 10mg PO daily x 35 days for DVT/PE prevention
- Wound care: Keep incision clean and dry. Monitor for signs of infection (erythema, purulent drainage, dehiscence)
- Pain management: Oxycodone 5mg PO q4-6h PRN. Avoid NSAIDs due to bleeding risk
- PT: WBAT with walker. Progress to cane per PT recommendation
- Follow-up: Orthopedic clinic in 2 weeks for suture removal and radiographic assessment"""
    },
    {
        "name": "Diabetes",
        "input": """Type 2 diabetes discharge: Continue metformin 500mg BID with meals. Monitor blood glucose fasting and 2 hours post-prandial. Target range 80-130 mg/dL fasting, <180 mg/dL postprandial. Diabetic diet: carbohydrate counting, limit simple sugars. Daily foot inspection for ulcers, calluses, or color changes. Follow-up endocrinology in 1 month."""
    },
    {
        "name": "Heart Failure",
        "input": """Congestive heart failure discharge: Fluid restriction 1.5-2L daily. Daily weights at same time, report gain >2-3 lbs in 24hr or >5 lbs in week. Continue furosemide 40mg daily, carvedilol 6.25mg BID, lisinopril 10mg daily. Low sodium diet <2g daily. Call for: severe dyspnea, chest pain, rapid weight gain, edema worsening."""
    },
    {
        "name": "Wound Care",
        "input": """Post-surgical wound care: Change dressing daily. Cleanse with normal saline, pat dry, apply antibiotic ointment if prescribed. Keep wound clean and dry. Monitor for infection signs: erythema, increased warmth, purulent drainage, dehiscence, fever >100.4F. Avoid soaking in water until cleared by surgeon. Activity restrictions: no heavy lifting >10 lbs x 2 weeks."""
    }
]


# ============================================================
# EXECUTION LOOP
# ============================================================

print("="*70)
print("TEST B‑v2 — Architecture B Pipeline (Deterministic Stage 1 → MedGemma Stage 2)")
print("="*70)

for idx, scenario in enumerate(scenarios, start=1):
    print("\n" + "="*70)
    print(f"Scenario {idx}/5: {scenario['name']}")
    print("="*70)

    # -----------------------------
    # Stage 1: Deterministic Normalize
    # -----------------------------
    normalized = deterministic_normalize(scenario["input"])

    print("\nSTAGE 1 OUTPUT (Deterministic Normalizer):")
    print("-"*70)
    print(normalized)
    print("-"*70)

    # -----------------------------
    # Stage 2: MedGemma Transformation
    # -----------------------------
    full_prompt = TRANSFORMER_PROMPT + normalized

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": full_prompt}]
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)

    input_len = inputs["input_ids"].shape[-1]

    print("\nGenerating Stage 2 transformed output...\n")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=700,
            do_sample=False,
        )

    outputs = outputs[0][input_len:]
    result = processor.decode(outputs, skip_special_tokens=True).strip()

    print("STAGE 2 OUTPUT (Final Patient Instructions):")
    print("-"*70)
    print(result if result else "No output generated")
    print("-"*70)
