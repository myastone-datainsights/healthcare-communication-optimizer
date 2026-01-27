"""
Test B-v4: Single-Scenario Isolation Test
Date: January 24, 2026
Environment: Kaggle GPU T4 x2

Hypothesis: MedGemma's discharge instruction capability works best when
processing ONE scenario at a time, not batching multiple scenarios.

Strategy: Test each discharge scenario independently to eliminate context
bleed and model state contamination.

Best practices incorporated:
- Stage 1: Deterministic normalizer (from B-v2)
- Stage 2: Reading level transformation (from A-v6 successful elements)
- Sentence length: 8-15 words
- Adult tone preservation
- No reasoning exposure
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

# Stage 2 Transformation Prompt (best elements from A-v6)
TRANSFORMATION_PROMPT = """Transform this structured clinical information into patient-level discharge instructions.

TARGET READING LEVEL: 5th grade (4.5-5.5 range)

SENTENCE REQUIREMENTS:
- Use 8-15 word sentences
- Vary sentence length naturally
- Use everyday words, avoid medical jargon
- Maintain adult-appropriate tone (not childish)

OUTPUT STRUCTURE:
**MEDICATION**
[Medication name and instructions in simple language]

**WHAT TO DO / WHAT NOT TO DO**
[4-5 clear action items, one per line]

**CALL DOCTOR RIGHT AWAY IF**
[Exactly 4 observable emergency signs, no repetition]

CRITICAL RULES:
- Do NOT add information not present in the input
- Do NOT expose reasoning process
- Do NOT repeat the same phrase
- Do NOT use medical terminology

Input to transform:
"""

# Stage 1: Deterministic Normalizer (from B-v2)
def normalize_content(clinical_input):
    """Stage 1: Parse and normalize clinical input into structured format"""
    # Simple deterministic parser
    normalized = {
        "medication": [],
        "care_instructions": [],
        "urgent_signs": []
    }
    
    lines = clinical_input.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('-'):
            continue
        normalized["care_instructions"].append(line)
    
    # Format for Stage 2
    output = "**MEDICATION**\n"
    output += clinical_input if "mg" in clinical_input.lower() else ""
    output += "\n\n**CARE INSTRUCTIONS**\n"
    output += clinical_input
    output += "\n\n**URGENT WARNING SIGNS**\n"
    output += "Monitor for concerning symptoms."
    
    return output

# Single scenario to test
SCENARIO_NAME = "Wound Care" 
BASELINE_GRADE = 8.6  

CLINICAL_INPUTS = {
    
    "Wound Care": """Post-surgical wound care: Change dressing daily. Cleanse with normal saline, pat dry, apply antibiotic ointment if prescribed. Keep wound clean and dry. Monitor for infection signs: erythema, increased warmth, purulent drainage, dehiscence, fever >100.4F. Avoid soaking in water until cleared by surgeon. Activity restrictions: no heavy lifting >10 lbs x 2 weeks."""
}

clinical_input = CLINICAL_INPUTS[SCENARIO_NAME]

print("="*70)
print(f"TEST B-v3: ISOLATED SCENARIO TEST - {SCENARIO_NAME}")
print("="*70)
print("\nSTAGE 1: Content Normalization")
print("-"*70)

# Stage 1: Normalize
stage1_output = normalize_content(clinical_input)
print(stage1_output)

print("\n" + "="*70)
print("STAGE 2: Reading Level Transformation")
print("="*70)

# Stage 2: Transform
full_prompt = TRANSFORMATION_PROMPT + stage1_output

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

print("\nGenerating patient-level output...\n")

with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        max_new_tokens=1000,
        do_sample=False,
    )
    outputs = outputs[0][input_len:]

result = processor.decode(outputs, skip_special_tokens=True).strip()

print("FINAL OUTPUT:")
print("-"*70)
print(result if result else "⚠ No output generated")
print("-"*70)

# Calculate metrics
if result:
    grade = textstat.flesch_kincaid_grade(result)
    reduction = BASELINE_GRADE - grade
    target_met = 4.5 <= grade <= 5.5
    
    # Check for hallucination markers
    has_repetition = len(result.split()) != len(set(result.split()))
    has_reasoning = "<unused" in result or "thought" in result.lower()[:100]
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"Scenario:           {SCENARIO_NAME}")
    print(f"Baseline Grade:     {BASELINE_GRADE}")
    print(f"Transformed Grade:  {grade:.1f}")
    print(f"Reduction:          {reduction:.1f} grades")
    print(f"Target Met:         {'✓ YES' if target_met else '✗ NO'}")
    print(f"Hallucination:      {'⚠ YES' if has_repetition else '✓ NO'}")
    print(f"Reasoning Leak:     {'⚠ YES' if has_reasoning else '✓ NO'}")
    print("="*70)
    
    # Guidance for next run
    print("\n📝 NEXT STEP:")
    print("Change SCENARIO_NAME and BASELINE_GRADE variables above")
    print("Run again with next scenario to test isolation hypothesis")
    print("\nScenarios remaining:")
    for name, baseline in [("Acetaminophen", 9.5), ("Diabetes", 10.2), 
                            ("Heart Failure", 9.7), ("Wound Care", 8.6)]:
        if name != SCENARIO_NAME:
            print(f"  - {name} (baseline: {baseline})")
else:
    print("\n⚠ ERROR: No output generated")

print("\n" + "="*70)