"""
Test A: Reading Level Optimization (Run 3 Prompt Framework)
Date: January 20, 2026
Environment: Kaggle GPU T4 x2
Goal: Achieve 4.5-5.5 grade level across 5 discharge scenarios

Prompt Strategy:
- Red flag minimalist framework
- 5-10 word sentences
- Critical warnings only
- Observable symptoms (no medical jargon)

Expected Outcome:
- Target: 4.5-5.5 grade level
- Potential issue: May lack dignity/naturalness (addressed in Test B)

Test Battery:
1. Acetaminophen (medication)
2. Hip Surgery (procedure)
3. Diabetes (chronic condition)
4. Heart Failure (chronic condition)
5. Wound Care (post-surgical)
"""

"""
Test A: Reading Level Optimization (Run 3 Prompt)
Goal: Achieve 4.5-5.5 grade level across all 5 scenarios
Focus: Red flag minimalist framework
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

# Run 3 Transformation Prompt (Red Flag Minimalist)
TRANSFORMATION_PROMPT = """Transform this clinical discharge instruction into patient-level guidance.

CRITICAL REQUIREMENTS:
- Use extremely short sentences (5-10 words each)
- Target 4th-5th grade reading level
- Focus ONLY on critical actions and life-threatening warnings
- Use common everyday words only

STRUCTURE:
1. MEDICATION (if applicable):
   - What to take, when, how much
   - Maximum daily limit
   - Critical interaction (alcohol, other drugs)
   
2. WHAT TO DO / WHAT NOT TO DO:
   - 3-5 simple action items
   - Use "Do" and "Don't" format
   
3. CALL DOCTOR RIGHT AWAY IF:
   - List 3-5 emergency signs patients can see/feel
   - Observable symptoms only (no medical terms)

EXCLUDE:
- Medical terminology
- "Why" explanations  
- General reassurance
- Non-critical warnings

RED FLAG WARNINGS ONLY:
Include only life-threatening or hospitalization-risk information.

Clinical Input:
"""

# Test scenarios with clinical inputs
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
print("TEST A: READING LEVEL OPTIMIZATION (RUN 3 PROMPT)")
print("="*70)
print("\n")

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
    
    print("\nGenerating transformed output...\n")
    
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
        baseline = [9.5, 9.6, 10.2, 9.7, 8.6][idx-1]  # Baseline grades
        reduction = baseline - grade
        
        print(f"\nBaseline Reading Level: {baseline}")
        print(f"Transformed Reading Level: {grade:.1f}")
        print(f"Grade Reduction: {reduction:.1f}")
        
        status = "✓ TARGET MET" if 4.5 <= grade <= 5.5 else "⚠ OUTSIDE TARGET"
        print(f"Status: {status}")
        
        results.append({
            "scenario": scenario["name"],
            "baseline": baseline,
            "transformed": grade,
            "reduction": reduction,
            "target_met": 4.5 <= grade <= 5.5
        })
    
    print("\n")

# Summary table
print("\n" + "="*70)
print("TEST A SUMMARY: READING LEVEL OPTIMIZATION")
print("="*70)
print("\nScenario          | Baseline | Transformed | Reduction | Target Met")
print("-"*70)
for r in results:
    status = "✓" if r["target_met"] else "✗"
    print(f"{r['scenario']:<17} | {r['baseline']:<8} | {r['transformed']:<11.1f} | {r['reduction']:<9.1f} | {status}")

avg_baseline = sum(r["baseline"] for r in results) / len(results)
avg_transformed = sum(r["transformed"] for r in results) / len(results)
avg_reduction = avg_baseline - avg_transformed
target_count = sum(1 for r in results if r["target_met"])

print("-"*70)
print(f"AVERAGE          | {avg_baseline:<8.1f} | {avg_transformed:<11.1f} | {avg_reduction:<9.1f} | {target_count}/5")
print("\n" + "="*70)