"""
MedGemma Universal Prompt Test Script
Purpose: Validate a single universal prompt across multiple discharge scenarios
"""

import os
from dotenv import load_dotenv
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
import textstat  # For readability scoring

# Load environment variables
load_dotenv()

# Set reproducibility seed
torch.manual_seed(42)


def load_model():
    """Load MedGemma model and processor"""
    print("Loading MedGemma 1.5 4B...")

    model_id = "google/medgemma-1.5-4b-it"

    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        dtype=torch.bfloat16,
        device_map="auto",
    )

    processor = AutoProcessor.from_pretrained(model_id)

    print("✓ Model loaded successfully")
    print(f"Running on device: {model.device}")

    if model.device.type == "cpu":
        print("⚠ Running on CPU. This will be slow for long outputs.")

    return model, processor


def transform_text(model, processor, clinical_text, prompt_instructions):
    """Transform clinical text using MedGemma"""

    full_prompt = f"""{prompt_instructions}

ORIGINAL DISCHARGE INSTRUCTIONS:
{clinical_text}

PATIENT-FRIENDLY VERSION:"""

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": full_prompt}],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device, dtype=torch.bfloat16)

    input_len = inputs["input_ids"].shape[-1]

    print("Generating transformation...")

    with torch.inference_mode():
        generation = model.generate(
            **inputs,
            max_new_tokens=1000,
            do_sample=False,
        )
        generation = generation[0][input_len:]

    output = processor.decode(generation, skip_special_tokens=True).strip()

    if not output:
        return "⚠ No output generated. Check model or prompt formatting."

    return output


def calculate_readability(text):
    """Calculate Flesch-Kincaid Grade Level"""
    try:
        return textstat.flesch_kincaid_grade(text)
    except Exception:
        return None


def run_test_example(model, processor, test_name, clinical_input, prompt_instructions):
    """Run a single test and display results"""

    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)

    print("\n--- CLINICAL INPUT ---")
    print(clinical_input)

    original_grade = calculate_readability(clinical_input)

    output = transform_text(model, processor, clinical_input, prompt_instructions)

    print("\n--- TRANSFORMED OUTPUT ---\n")
    print(output)

    transformed_grade = calculate_readability(output)

    print("\n--- READABILITY METRICS ---")
    if original_grade is not None:
        print(f"Original Grade Level: {original_grade:.1f}")
    else:
        print("Original Grade Level: Unable to calculate")

    if transformed_grade is not None:
        print(f"Transformed Grade Level: {transformed_grade:.1f}")
    else:
        print("Transformed Grade Level: Unable to calculate")

    if original_grade is not None and transformed_grade is not None:
        improvement = original_grade - transformed_grade
        print(f"Improvement: {improvement:.1f} grade levels")

        if transformed_grade <= 5.0:
            print("✓ Target range achieved (4th–5th grade)")
        elif transformed_grade <= 6.0:
            print("⚠ Close to target (slightly above 5th grade)")
        else:
            print("✗ Above target range (needs refinement)")

    print("\n")


# ---------------------------------------------------------
# UNIVERSAL PATIENT-FRIENDLY DISCHARGE INSTRUCTION PROMPT
# ---------------------------------------------------------

UNIVERSAL_PATIENT_PROMPT = """
You are a patient communication specialist. Transform these clinical discharge instructions into clear, respectful guidance patients can act on.

GOAL:
Create a patient-friendly version at a 4.5–5.5 grade reading level. Keep tone dignified, direct, and calm.

STRUCTURE (Use all sections; fill only with relevant content):

1. MEDICATIONS:
   List each medication separately.
   Use patient-friendly labels:
   - “your blood thinner medication (rivaroxaban)”
   - “your pain medication (oxycodone)”
   - “your fever medication (acetaminophen)”
   - “your antibiotic (amoxicillin)”
   Format: what it is, when to take it, how much, and one critical safety warning.

2. DAILY CARE:
   What the patient must do each day.
   Examples: wound care, movement rules, breathing exercises, checking for swelling.
   Use 2–4 short, clear sentences.

3. WHAT NOT TO DO:
   List 3–5 specific actions to avoid.
   Use format: “Don’t [action].”
   Add brief real-world examples in parentheses when helpful.

4. WATCH FOR PROBLEMS:
   List 3–5 warning signs to check for daily.
   Use concrete symptoms patients can see or feel.

5. CALL YOUR DOCTOR RIGHT AWAY IF:
   List 4–6 emergency symptoms.
   Always include:
   - chest pain
   - trouble breathing
   - heavy bleeding
   Add condition-specific emergencies from the input.

6. FOLLOW-UP:
   When the next appointment is and what will happen there.

WRITING STYLE:
- Use short, clear sentences (8–12 words each).
- Some sentences shorter (5–6 words), some longer (12–15 words).
- Use “you” and “your” throughout.
- Be direct and action-oriented.
- Add helpful examples: “every 6 hours (morning, afternoon, evening, bedtime).”
- Keep tone respectful and calm.

MEDICATION NAMING RULES:
- Prescription meds: “your [function] medication (clinical name)”
- Over-the-counter meds: “generic name (Brand name or store brand)”
This rule is required for every medication.

RED FLAG WARNINGS ONLY:
Include only life-threatening or hospitalization-risk information:
- blood clots
- infection
- bleeding
- overdose
- breathing problems
- chest pain
- yellow skin or eyes
- severe stomach pain
- critical drug interactions (e.g., alcohol + acetaminophen)

EXCLUDE:
- general side effects
- allergy warnings
- pregnancy precautions
- reassurance statements
- “why” explanations
- environmental setup advice
- repeated instructions

Keep the final output clear, respectful, and easy to follow.
"""


def main():
    """Main test execution"""

    print("\n🔧 MedGemma Universal Prompt Testing - Test Run 5")
    print("=" * 70)

    model, processor = load_model()

    # -------------------------
    # Test 1: Acetaminophen
    # -------------------------
    clinical_input_1 = (
        "Administer 500mg acetaminophen PO q6h PRN for pain. "
        "Monitor for hepatotoxicity."
    )

    run_test_example(
        model,
        processor,
        "Acetaminophen (Medication Management)",
        clinical_input_1,
        UNIVERSAL_PATIENT_PROMPT,
    )

    # -------------------------
    # Test 2: Hip Surgery
    # -------------------------
    clinical_input_2 = """Post-operative total hip arthroplasty discharge protocol:
- Maintain hip precautions: avoid flexion >90°, adduction past midline, and internal rotation
- Prophylactic anticoagulation: Rivaroxaban 10mg PO daily x 35 days for DVT/PE prevention
- Wound care: Keep incision clean and dry. Monitor for signs of infection (erythema, purulent drainage, dehiscence)
- Pain management: Oxycodone 5mg PO q4-6h PRN. Avoid NSAIDs due to bleeding risk
- PT: WBAT with walker. Progress to cane per PT recommendation
- Follow-up: Orthopedic clinic in 2 weeks for suture removal and radiographic assessment"""

    run_test_example(
        model,
        processor,
        "Hip Surgery (Post-Surgical Care)",
        clinical_input_2,
        UNIVERSAL_PATIENT_PROMPT,
    )

    print("=" * 70)
    print("✓ Universal prompt testing complete - Test Run 5")
    print("=" * 70)


if __name__ == "__main__":
    main()
