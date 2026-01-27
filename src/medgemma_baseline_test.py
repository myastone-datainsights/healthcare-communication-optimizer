"""
MedGemma Baseline Discharge Instruction Test
Purpose: Evaluate whether MedGemma can generate discharge instructions
from a minimal structured prompt.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import textstat

# Reproducibility
torch.manual_seed(42)

# -----------------------------
# Load MedGemma (GPU optimized)
# -----------------------------
model_id = "google/medgemma-1.5-4b-it"

print("Loading MedGemma 1.5 4B on GPU...")

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
)

print(f"Model loaded successfully on {model.device}")


# -----------------------------
# Transformation Function
# -----------------------------
def transform_text(model, tokenizer, clinical_text, prompt_instructions):
    """Transform clinical text using MedGemma"""

    full_prompt = f"""{prompt_instructions}

{clinical_text}
"""

    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

    print("Generating output...")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=600,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Remove the prompt from output
    output = output.replace(full_prompt, "").strip()

    if not output:
        return "No output generated. Check model or prompt formatting."

    return output


# -----------------------------
# Readability Helper
# -----------------------------
def calculate_readability(text):
    """Calculate Flesch-Kincaid Grade Level"""
    try:
        return textstat.flesch_kincaid_grade(text)
    except Exception:
        return None


# -----------------------------
# Test Runner
# -----------------------------
def run_test_example(model, tokenizer, test_name, clinical_input, prompt_instructions):
    """Run a single test and display results"""

    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)

    print("\n--- PROMPT SENT TO MODEL ---")
    print(prompt_instructions)

    output = transform_text(model, tokenizer, clinical_input, prompt_instructions)

    print("\n--- MODEL OUTPUT ---\n")
    print(output)

    grade = calculate_readability(output)

    print("\n--- READABILITY METRICS ---")
    if grade is not None:
        print(f"Output Grade Level: {grade:.1f}")
    else:
        print("Output Grade Level: Unable to calculate")

    print("\n")


# ---------------------------------------------------------
# BASELINE DISCHARGE INSTRUCTION GENERATION PROMPT
# ---------------------------------------------------------

BASELINE_PROMPT = """You are a clinical communication assistant.

Rewrite the following into a full patient discharge instruction:

Acetaminophen 500mg for post-surgical pain management.
Take 1-2 tablets every 6 hours as needed.
Do not exceed 4000mg in 24 hours.
Avoid alcohol."""


# -----------------------------
# Main Execution
# -----------------------------
def main():
    print("\nMedGemma Baseline Discharge Instruction Test")
    print("=" * 70)

    clinical_input = ""  # No additional text needed

    run_test_example(
        model,
        tokenizer,
        "Baseline Discharge Instruction Generation",
        clinical_input,
        BASELINE_PROMPT,
    )

    print("=" * 70)
    print("Baseline discharge instruction test complete")
    print("=" * 70)


main()
