import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

# Get HF token
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HUGGINGFACE_TOKEN")

torch.manual_seed(42)

model_id = "google/medgemma-1.5-4b-it"

print("Loading MedGemma 1.5 4B ... ")

processor = AutoProcessor.from_pretrained(model_id, token=hf_token)
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    token=hf_token,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

print(f"\nModel loaded on {model.device}\n")


# ============================================================
# STAGE 1 — CONTENT NORMALIZER (Architecture B – Step 1)
# ============================================================

NORMALIZER_PROMPT = """
Normalize the density, structure, and organization of the following clinical discharge instructions.

GOAL:
Produce a standardized, clinically accurate, medium-density version of the instructions that prepares the text for reading-level transformation in Stage 2.

ABSOLUTE RULE:
Do NOT simplify language. Do NOT reduce reading level. Do NOT change tone. Do NOT add new clinical facts.

CLINICAL ACCURACY:
- Keep all medications, doses, timing, and limits
- Keep all monitoring steps
- Keep all wound-care steps
- Keep all activity restrictions
- Keep all red-flag symptoms
- Keep all follow-up instructions

DENSITY NORMALIZATION:
- Expand overly compressed content
- Condense overly verbose content
- Remove redundancy
- Ensure each section contains 5–8 medium-length sentences
- One clinical action per sentence

STRUCTURE (ONLY these three sections):

1. **MEDICATION**
- All medications, doses, timing, limits
- One safety warning per medication class

2. **CARE INSTRUCTIONS**
- Wound care
- Activity restrictions
- Diet instructions
- Monitoring steps
- Daily routines

3. **URGENT WARNING SIGNS**
- All red-flag symptoms
- All “call your doctor” triggers
- No more than 6–8 items
- No repetition

REMOVE:
- Reassurance language
- Filler phrases (“as instructed”, “as directed”)
- Duplicate warnings
- Duplicate steps

EXPAND IF NEEDED:
If the input is sparse, expand implied steps (e.g., “take with water”, “store safely”) ONLY if clinically implied by the original text.

DO NOT:
- Add new medical conditions
- Add new medications
- Add new red-flag symptoms
- Show reasoning or planning
- Output anything except the normalized content

Clinical Input:
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

print("="*70)
print("STAGE 1 — CONTENT NORMALIZER (Architecture B – Step 1)")
print("="*70)
print("\n")


# ============================================================
# Generation Loop
# ============================================================

for idx, scenario in enumerate(scenarios, start=1):
    print("="*70)
    print(f"Scenario {idx}/5: {scenario['name']}")
    print("="*70)

    full_prompt = NORMALIZER_PROMPT + scenario["input"]

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": full_prompt}
            ]
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

    print("Generating normalized output ...\n")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=700,
            do_sample=False,
        )

    outputs = outputs[0][input_len:]
    result = processor.decode(outputs, skip_special_tokens=True).strip()

    print("NORMALIZED OUTPUT:")
    print("-"*70)
    print(result if result else "No output generated")
    print("-"*70)
    print("\n")
