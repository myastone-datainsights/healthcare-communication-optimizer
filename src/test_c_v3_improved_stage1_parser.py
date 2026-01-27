"""
Test C-v3: Improved Stage 1 Content Parser
Date: January 25, 2026
Environment: Kaggle GPU T4 x2

Improvement over Test B series:
- Intelligent deterministic parser (no more duplication)
- Proper section extraction (medication, instructions, warnings)
- Preserves all clinical content (no vague placeholders)
- Prevents hallucinations (Stage 2 works with complete information)

Strategy: Hybrid rule-based + regex parser
- Medication: Detected by dosage patterns (mg, tablet, etc.)
- Instructions: Care directions, precautions, follow-up
- Warnings: Emergency signs, when to call doctor
"""

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
import textstat
import re

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
# STAGE 1: IMPROVED CONTENT PARSER
# ============================================================================

def normalize_content_v2(clinical_input):
    """
    Intelligent deterministic parser for clinical discharge instructions.
    
    Extracts and organizes:
    - Medications (drugs, dosages, frequencies, interactions)
    - Care instructions (precautions, activities, follow-up)
    - Warning signs (when to contact provider)
    
    Returns structured format that prevents Stage 2 hallucinations.
    """
    
    sections = {
        "medication": [],
        "instructions": [],
        "warnings": []
    }
    
    # Split on periods and dashes to get individual statements
    statements = re.split(r'[.\-]', clinical_input)
    
    for statement in statements:
        statement = statement.strip()
        if not statement or len(statement) < 10:  # Skip very short fragments
            continue
        
        # MEDICATION DETECTION
        # Look for: dosage (mg, tablet), drug names, frequencies
        medication_indicators = [
            r'\d+\s*mg',           # "500mg", "40 mg"
            r'tablet',
            r'daily|BID|twice|TID|QID|q\d+',  # Frequencies
            r'take|continue|prescribed',
            r'alcohol|NSAID'       # Interactions
        ]
        
        if any(re.search(pattern, statement, re.IGNORECASE) for pattern in medication_indicators):
            sections["medication"].append(statement.strip())
            continue
        
        # WARNING DETECTION
        # Look for: emergency language, contact instructions
        warning_indicators = [
            r'call|contact|notify',
            r'if\s+(you|pain|fever|symptoms?)',
            r'signs? of',
            r'emergency|urgent|severe|sudden',
            r'report|monitor for'
        ]
        
        if any(re.search(pattern, statement, re.IGNORECASE) for pattern in warning_indicators):
            sections["warnings"].append(statement.strip())
            continue
        
        # CARE INSTRUCTIONS (everything else)
        # Precautions, activities, diet, follow-up
        sections["instructions"].append(statement.strip())
    
    # Build structured output
    output = "**MEDICATION**\n"
    if sections["medication"]:
        output += " ".join(sections["medication"])
    else:
        output += "No specific medication instructions provided."
    
    output += "\n\n**CARE INSTRUCTIONS**\n"
    if sections["instructions"]:
        output += " ".join(sections["instructions"])
    else:
        output += "Follow standard post-care guidelines as directed."
    
    output += "\n\n**URGENT WARNING SIGNS**\n"
    if sections["warnings"]:
        output += " ".join(sections["warnings"])
    else:
        output += "Contact your provider if you have concerns about your recovery."
    
    return output

# ============================================================================
# STAGE 2: READING LEVEL TRANSFORMATION
# ============================================================================

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
[Exactly 4 observable emergency signs from the input, no repetition]

CRITICAL RULES:
- Use ONLY information provided in the input below
- Do NOT add warnings, symptoms, or instructions not present in input
- Do NOT expose reasoning process
- Do NOT repeat the same phrase
- Do NOT use medical terminology

Input to transform:
"""

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Single scenario to test 
SCENARIO_NAME = "Diabetes" 
BASELINE_GRADE = 10.2  

CLINICAL_INPUTS = {    
    "Diabetes": """Type 2 diabetes discharge: Continue metformin 500mg BID with meals. Monitor blood glucose fasting and 2 hours post-prandial. Target range 80-130 mg/dL fasting, <180 mg/dL postprandial. Diabetic diet: carbohydrate counting, limit simple sugars. Daily foot inspection for ulcers, calluses, or color changes. Follow-up endocrinology in 1 month.""",
}

clinical_input = CLINICAL_INPUTS[SCENARIO_NAME]

# ============================================================================
# EXECUTE PIPELINE
# ============================================================================

print("="*70)
print(f"TEST C-v1: IMPROVED STAGE 1 PARSER - {SCENARIO_NAME}")
print("="*70)
print("\nSTAGE 1: Intelligent Content Parsing")
print("-"*70)

# Stage 1: Parse and normalize
stage1_output = normalize_content_v2(clinical_input)
print(stage1_output)

print("\n" + "="*70)
print("STAGE 2: Reading Level Transformation")
print("="*70)

# Stage 2: Transform to patient level
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
    
    # Compare output to input for hallucination detection
    stage1_words = set(stage1_output.lower().split())
    output_words = set(result.lower().split())
    
    # Check if output contains many words not in Stage 1
    new_words = output_words - stage1_words
    common_words = {'the', 'a', 'an', 'to', 'if', 'you', 'your', 'do', 'not', 'have', 'or', 'and'}
    significant_new_words = new_words - common_words
    hallucination_risk = len(significant_new_words) > 15  # Threshold for concern
    
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
    print(f"Hallucination Risk:   {'⚠ HIGH' if hallucination_risk else '✓ LOW'}")
    if hallucination_risk:
        print(f"  New words added: {len(significant_new_words)}")
    print("="*70)
    
    # Comparison to B-series results
    b_series_results = {
        "Acetaminophen": 5.8,
        "Hip Surgery": 4.8,
        "Diabetes": 5.1,
        "Heart Failure": 3.5,
        "Wound Care": 3.6
    }
    
    if SCENARIO_NAME in b_series_results:
        b_result = b_series_results[SCENARIO_NAME]
        improvement = abs(4.95 - grade) - abs(4.95 - b_result)  # Distance from target midpoint
        print(f"\n📊 COMPARISON TO TEST B-v{['3','4','5','6','7'][list(b_series_results.keys()).index(SCENARIO_NAME)]}:")
        print(f"Previous Result: {b_result}")
        print(f"Current Result:  {grade:.1f}")
        print(f"Improvement:     {'✓ Better' if improvement < 0 else '✗ Worse' if improvement > 0 else '→ Same'}")
        if target_met and not (4.5 <= b_result <= 5.5):
            print("🎉 NOW MEETS TARGET (previously did not)")
    
    # Guidance for next run
    print("\n📝 NEXT STEP:")
    print("Change SCENARIO_NAME and BASELINE_GRADE variables above")
    print("Run again with next scenario to validate Stage 1 improvements")
    print("\nScenarios to test:")
    for name, baseline in [("Acetaminophen", 9.5), ("Hip Surgery", 9.6), ("Diabetes", 10.2), 
                            ("Heart Failure", 9.7), ("Wound Care", 8.6)]:
        if name != SCENARIO_NAME:
            print(f"  - {name} (baseline: {baseline})")
else:
    print("\n⚠ ERROR: No output generated")

print("\n" + "="*70)