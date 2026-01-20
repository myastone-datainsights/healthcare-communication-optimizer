import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
import textstat

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
# A‑v6 TRANSFORMATION PROMPT (Stabilized, No Dignity Layer Yet)
# ============================================================

TRANSFORMATION_PROMPT = """
Transform this clinical discharge instruction into patient-level guidance.

GOAL:
Produce clear, simple instructions at a 4.5–5.5 grade reading level.

ABSOLUTE RULE:
Do NOT show your reasoning, planning, steps, or thoughts.
Produce ONLY the final patient instructions.

SENTENCE RULES:
- Use short, clear sentences (10–16 words each)
- Acceptable range: 8–18 words per sentence
- Do NOT use very short phrases like “Rest your body” or “You feel very sick”

LANGUAGE RULES:
- Use everyday words only (no medical terms unless unavoidable)
- Use clear adult language with simple vocabulary
- Avoid complex phrases like “potential side effects”, “specific recommendations”,
  “as directed by your doctor”, “as instructed”, “follow the instructions on the label”

CONTENT PRESERVATION:
- Keep ALL essential actions and warnings
- Do NOT remove any clinical step unless clearly non-essential
- Do NOT merge multiple steps into one sentence
- Keep all medication names, doses, and monitoring steps when present
- Do NOT add new warnings or new risks that are not in the original text
- Do NOT repeat the same warning in different words

CONTENT FLOOR:
- Each section must contain 6–8 sentences

STRUCTURE (ONLY these three sections, no extras):

1. MEDICATION (if applicable):
- What to take
- When to take it
- How much to take
- Maximum daily amount
- One key safety warning

2. WHAT TO DO / WHAT NOT TO DO:
- 4–8 clear action steps
- Use simple verbs (“Do…”, “Do not…”)

3. CALL DOCTOR RIGHT AWAY IF:
- List EXACTLY 3 urgent signs the patient can see or feel
- No repetition
- No medical terminology
- No open-ended lists

AVOID:
- Reassurance
- Explanations of “why”
- Long sentences beyond the allowed range
- Lists longer than required
- Extra sections (do NOT add new headings)
- New warnings or risks not present in the original text

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

results = []

print("="*70)
print("TEST A-v6: READING LEVEL OPTIMIZATION (STABILIZED)")
print("="*70)
print("\n")


# ============================================================
# Generation Loop
# ============================================================

for idx, scenario in enumerate(scenarios, start=1):
    print("="*70)
    print(f"Scenario {idx}/5: {scenario['name']}")
    print("="*70)

    full_prompt = TRANSFORMATION_PROMPT + scenario["input"]

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

    print("Generating transformed output ...\n")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=600,
            do_sample=False,
        )

    outputs = outputs[0][input_len:]
    result = processor.decode(outputs, skip_special_tokens=True).strip()

    print("TRANSFORMED OUTPUT:")
    print("-"*70)
    print(result if result else "No output generated")
    print("-"*70)

    if result:
        grade = textstat.flesch_kincaid_grade(result)
        baseline = [9.5, 9.6, 10.2, 9.7, 8.6][idx-1]
        reduction = baseline - grade

        print(f"Baseline Reading Level: {baseline}")
        print(f"Transformed Reading Level: {grade:.1f}")
        print(f"Grade Reduction: {reduction:.1f}")

        status = "✓ TARGET MET" if 4.5 <= grade <= 5.5 else "✗ OUTSIDE TARGET"
        print(f"Status: {status}")

        results.append({
            "scenario": scenario["name"],
            "baseline": baseline,
            "transformed": grade,
            "reduction": reduction,
            "target_met": 4.5 <= grade <= 5.5
        })

    print("\n")


# ============================================================
# Summary Table
# ============================================================

print("="*70)
print("TEST A-v6 SUMMARY: READING LEVEL OPTIMIZATION")
print("="*70)
print("Scenario           | Baseline | Transformed | Reduction | Target")
print("-"*70)

for r in results:
    status = "✓" if r["target_met"] else "✗"
    print(f"{r['scenario']:<18} | {r['baseline']:<8} | {r['transformed']:<11.1f} | {r['reduction']:<9.1f} | {status}")

avg_baseline = sum(r["baseline"] for r in results) / len(results)
avg_transformed = sum(r["transformed"] for r in results) / len(results)
avg_reduction = avg_baseline - avg_transformed
target_count = sum(1 for r in results if r["target_met"])

print("-"*70)
print(f"AVERAGE           | {avg_baseline:<8.1f} | {avg_transformed:<11.1f} | {avg_reduction:<9.1f} | {target_count}/5")
print("="*70)
