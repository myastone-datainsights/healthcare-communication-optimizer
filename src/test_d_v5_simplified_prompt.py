"""
Test D-v5: Simplified Prompt + No Stage 1 Parser
Date: January 25, 2026
Environment: Kaggle GPU T4 x2

Key Changes from C-series:
- REMOVED: Stage 1 parser (feed input directly to MedGemma)
- REMOVED: Grade-level framing ("5th grade", "4.5-5.5 range")
- ADDED: Adult-focused language ("any adult can understand")
- ADDED: Natural sentence variety guidance
- SIMPLIFIED: Direct transformation without preprocessing

Hypothesis: Grade-level framing triggers elementary tone. Removing it
and feeding clinical input directly may produce better results.
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

# ============================================================================
# TRANSFORMATION PROMPT (Simplified - No Grade-Level Language)
# ============================================================================

TRANSFORMATION_PROMPT = """Transform these discharge instructions into clear, patient-friendly format.

LANGUAGE REQUIREMENTS:
- Use simple, everyday words that any adult can understand
- Write sentences that are 8-15 words long
- Vary sentence length naturally (some shorter, some longer)
- Avoid medical jargon - use common terms instead
- Maintain a respectful, adult tone (not childish)

STRUCTURE:
**MEDICATION**
[Simple medication instructions - what to take, when, how much]

**WHAT TO DO / WHAT NOT TO DO**
[4-5 clear action items patients should follow]

**CALL DOCTOR RIGHT AWAY IF**
[Exactly 4 warning signs patients can see or feel]

CRITICAL RULES:
- Use ONLY information from the discharge instructions below
- Do NOT add symptoms, warnings, or advice not mentioned
- Do NOT repeat the same information
- Do NOT expose your reasoning process
- Do NOT use medical terminology

Discharge instructions to transform:

"""

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Single scenario to test
SCENARIO_NAME = "Wound Care"
BASELINE_GRADE = 8.6  

CLINICAL_INPUTS = {   
    "Wound Care": """Post-surgical wound care: Change dressing daily. Cleanse with normal saline, pat dry, apply antibiotic ointment if prescribed. Keep wound clean and dry. Monitor for infection signs: erythema, increased warmth, purulent drainage, dehiscence, fever >100.4F. Avoid soaking in water until cleared by surgeon. Activity restrictions: no heavy lifting >10 lbs x 2 weeks."""
}

clinical_input = CLINICAL_INPUTS[SCENARIO_NAME]

# ============================================================================
# EXECUTE TRANSFORMATION (Direct - No Stage 1)
# ============================================================================

print("="*70)
print(f"TEST D-v1: SIMPLIFIED PROMPT (NO STAGE 1) - {SCENARIO_NAME}")
print("="*70)
print("\nDIRECT TRANSFORMATION (No preprocessing)")
print("-"*70)

full_prompt = TRANSFORMATION_PROMPT + clinical_input

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

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

if result:
    grade = textstat.flesch_kincaid_grade(result)
    reduction = BASELINE_GRADE - grade
    target_met = 4.5 <= grade <= 5.5
    
    # Check for issues
    has_repetition = len(result.split()) != len(set(result.split()))
    has_reasoning = "<unused" in result or "thought" in result.lower()[:100]
    
    # Simple hallucination check: look for common invented phrases
    hallucination_phrases = [
        "rest your body", "drink plenty", "avoid driving",
        "confusion", "dizziness", "trouble breathing"
    ]
    likely_hallucination = any(phrase in result.lower() for phrase in hallucination_phrases)
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"Scenario:             {SCENARIO_NAME}")
    print(f"Baseline Grade:       {BASELINE_GRADE}")
    print(f"Transformed Grade:    {grade:.1f}")
    print(f"Reduction:            {reduction:.1f} grades")
    print(f"Target Met (4.5-5.5): {'✓ YES' if target_met else '✗ NO'}")
    print(f"Repetition Detected:  {'⚠ YES' if has_repetition else '✓ NO'}")
    print(f"Reasoning Leak:       {'⚠ YES' if has_reasoning else '✓ NO'}")
    print(f"Likely Hallucination: {'⚠ YES' if likely_hallucination else '✓ NO'}")
    print("="*70)
    
    # Comparison to previous tests
    previous_results = {
        "Acetaminophen": {"B": 5.8, "C": 7.3},
        "Hip Surgery": {"B": 4.8, "C": 5.4},
        "Diabetes": {"B": 5.1, "C": 4.4},
        "Heart Failure": {"B": 3.5, "C": 3.1},
        "Wound Care": {"B": 3.6, "C": 4.2}
    }
    
    if SCENARIO_NAME in previous_results:
        prev = previous_results[SCENARIO_NAME]
        print(f"\n📊 COMPARISON TO PREVIOUS TESTS:")
        print(f"B-series Result: {prev['B']}")
        print(f"C-series Result: {prev['C']}")
        print(f"D-v1 Result:     {grade:.1f}")
        
        # Determine if this is an improvement
        b_distance = abs(4.95 - prev['B'])  # Distance from target midpoint (4.95)
        c_distance = abs(4.95 - prev['C'])
        d_distance = abs(4.95 - grade)
        
        best_previous = min(b_distance, c_distance)
        
        if d_distance < best_previous:
            print(f"Status:          ✓ IMPROVED (closer to target)")
        elif target_met and not (4.5 <= prev['B'] <= 5.5) and not (4.5 <= prev['C'] <= 5.5):
            print(f"Status:          🎉 NOW MEETS TARGET (previously did not)")
        elif d_distance == best_previous:
            print(f"Status:          → SAME (no change)")
        else:
            print(f"Status:          ✗ WORSE (further from target)")
    
    print("\n📝 NEXT STEP:")
    print("Change SCENARIO_NAME and BASELINE_GRADE for next test")
    print("\nRemaining scenarios:")
    for name, baseline in [("Acetaminophen", 9.5), ("Hip Surgery", 9.6), 
                            ("Diabetes", 10.2), ("Heart Failure", 9.7), ("Wound Care", 8.6)]:
        if name != SCENARIO_NAME:
            print(f"  - {name} (baseline: {baseline})")
else:
    print("\n⚠ ERROR: No output generated")

print("\n" + "="*70)