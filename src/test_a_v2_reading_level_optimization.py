"""
Test A-v2: Reading Level Optimization (Architecture B - Two-Step)
Date: January 20, 2026
Environment: Kaggle GPU T4 x2

Goal: Achieve consistent 4.5-5.5 grade level WITHOUT hallucinations

Strategy Change:
- Architecture A (v1): Clinical input → Transform directly
- Architecture B (v2): Baseline output → Simplify existing content

This reduces hallucination risk by transforming proven clinical content
rather than generating new content from scratch.
"""

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
import textstat

# Get HF token
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HUGGINGFACE_TOKEN")

torch.manual_seed(42)

model_id = "google/medgemma-1.5-4b-it"

print("Loading MedGemma 1.5 4B...")

processor = AutoProcessor.from_pretrained(model_id, token=hf_token)
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    token=hf_token,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

print(f"✓ Model loaded on {model.device}\n")

# Simplification Prompt (Architecture B)
SIMPLIFICATION_PROMPT = """Simplify this discharge instruction to 5th grade reading level.
Preserve ALL medical information. Do not add new content.

REQUIREMENTS:
- Use 8-12 word sentences (range 6-15 acceptable)
- Target 5th grade reading level (4.5-5.5 range)
- Remove medical jargon, use everyday words
- Keep ALL warnings and medication information
- List exactly 4 emergency signs (no repetition)

FORMAT OUTPUT AS:
MEDICATION:
[Keep all medication info, simplify language]

WHAT TO DO / WHAT NOT TO DO:
[List 4-5 clear actions]

CALL DOCTOR RIGHT AWAY IF:
[Exactly 4 unique emergency signs, no repetition]

ORIGINAL DISCHARGE INSTRUCTION:
"""

# Baseline outputs from zero-shot tests (truncated for brevity - use first ~500 chars)
scenarios = [
    {
        "name": "Acetaminophen",
        "baseline": """## Patient Discharge Instructions: Acetaminophen 500mg

**Medication:** Acetaminophen 500mg (Tylenol)

**Purpose:** This medication is prescribed to help manage pain after your surgery.

**Dosage Instructions:**
* Take one (1) 500mg tablet by mouth every 6 hours as needed for pain.
* Do not exceed the maximum daily dose: Do not take more than 6 tablets (3000mg) in a 24-hour period.
* Take with food: Always take acetaminophen with food or milk to help prevent stomach upset.
* Do not crush or chew: Swallow the tablet whole."""
    },
    {
        "name": "Hip Surgery", 
        "baseline": """## Patient Discharge Instructions: Hip Replacement Surgery Recovery

**Important Information:**
Thank you for choosing us for your hip replacement surgery! We are committed to helping you recover safely and effectively.

**Immediate Post-Discharge Care (First 24-48 Hours):**
* Rest: Get plenty of rest, especially during the first few days. Avoid strenuous activities.
* Mobility: Walking: Start walking as soon as you are medically cleared. Begin with short, slow walks and gradually increase the distance and pace as tolerated.
* Pain Management: Take your prescribed pain medication regularly as directed.
* Ice: Apply ice packs to the surgical site for 15-20 minutes several times a day."""
    },
    {
        "name": "Diabetes",
        "baseline": """## Patient Discharge Instructions: Type 2 Diabetes Management

**1. Blood Sugar Monitoring:**
* Frequency: Check your blood sugar levels at least four times per day. This includes:
    * Upon waking up: Before taking any medication.
    * Before meals: (Breakfast, Lunch, Dinner)
    * Two hours after meals
* Target Range: Your target blood sugar range is generally 80-130 mg/dL when not eating, and below 180 mg/dL two hours after meals.

**2. Medication Management:**
Take medications as prescribed. Do not skip doses unless instructed by your doctor."""
    },
    {
        "name": "Heart Failure",
        "baseline": """## Patient Discharge Instructions: Congestive Heart Failure (CHF) Management

**1. Fluid Restriction:**
* Why: Excess fluid in your body can worsen heart failure symptoms like shortness of breath, swelling (edema), and fatigue.
* Limit your daily fluid intake to approximately 1.5 to 2 liters (about 5-6 cups) per day.

**2. Daily Weight Monitoring:**
* Weigh yourself daily at the same time each day.
* Report any significant weight gain (e.g., more than 2-3 pounds in a day or 5 pounds in a week) to your doctor immediately.

**3. Medication Management:**
Take all medications as prescribed."""
    },
    {
        "name": "Wound Care",
        "baseline": """## Patient Discharge Instructions: Post-Surgical Wound Care

**1. Wound Care:**
* Dressing Changes: Your surgeon will instruct you on when and how to change your dressing.
* Keep the Wound Clean and Dry: Keep the wound area clean and dry.
* Do Not Pick or Scratch: Avoid picking at scabs or scratching the wound.

**2. Signs of Infection:**
Contact your doctor immediately if you notice:
* Increased Redness: Redness spreading around the wound.
* Increased Pain: Pain that is worse than expected.
* Fever: A temperature of 100.4°F (38°C) or higher."""
    }
]

results = []

print("="*70)
print("TEST A-v2: SIMPLIFICATION OF BASELINE (ARCHITECTURE B)")
print("="*70)
print("\n")

for idx, scenario in enumerate(scenarios, start=1):
    print("="*70)
    print(f"Scenario {idx}/5: {scenario['name']}")
    print("="*70)
    
    full_prompt = SIMPLIFICATION_PROMPT + scenario["baseline"]
    
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
    
    print("\nGenerating simplified output...\n")
    
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1000,
            do_sample=False,
        )
        outputs = outputs[0][input_len:]
    
    result = processor.decode(outputs, skip_special_tokens=True).strip()
    
    print("SIMPLIFIED OUTPUT:")
    print("-"*70)
    print(result if result else "No output generated")
    print("-"*70)
    
    if result:
        grade = textstat.flesch_kincaid_grade(result)
        baseline_grades = [9.5, 9.6, 10.2, 9.7, 8.6]
        baseline = baseline_grades[idx-1]
        reduction = baseline - grade
        
        print(f"\nBaseline: {baseline} | Simplified: {grade:.1f} | Reduction: {reduction:.1f}")
        
        status = "✓ TARGET" if 4.5 <= grade <= 5.5 else "✗ OUTSIDE"
        print(f"Status: {status}")
        
        # Check for hallucination (repetition)
        words = result.lower().split()
        if len(words) != len(set(words)):
            repeated = [w for w in set(words) if words.count(w) > 3]
            if repeated:
                print(f"⚠ WARNING: Possible repetition detected: {repeated[:3]}")
        
        results.append({
            "scenario": scenario["name"],
            "baseline": baseline,
            "simplified": grade,
            "reduction": reduction,
            "target_met": 4.5 <= grade <= 5.5
        })
    
    print("\n")

# Summary
print("\n" + "="*70)
print("TEST A-v2 SUMMARY")
print("="*70)
print("\nScenario          | Baseline | Simplified | Reduction | Target")
print("-"*70)
for r in results:
    status = "✓" if r["target_met"] else "✗"
    print(f"{r['scenario']:<17} | {r['baseline']:<8} | {r['simplified']:<10.1f} | {r['reduction']:<9.1f} | {status}")

avg_baseline = sum(r["baseline"] for r in results) / len(results)
avg_simplified = sum(r["simplified"] for r in results) / len(results)
avg_reduction = avg_baseline - avg_simplified
target_count = sum(1 for r in results if r["target_met"])

print("-"*70)
print(f"AVERAGE          | {avg_baseline:<8.1f} | {avg_simplified:<10.1f} | {avg_reduction:<9.1f} | {target_count}/5")
print("\n" + "="*70)