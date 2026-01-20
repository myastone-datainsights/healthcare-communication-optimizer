# MedGemma Baseline Capability Assessment

## Purpose
Test whether MedGemma 1.5 4B can generate patient-friendly discharge instructions zero-shot, and establish baseline reading levels for comparison against transformation system.

## Test Environment
- **Platform:** Kaggle GPU T4 x2
- **Model:** google/medgemma-1.5-4b-it
- **Date:** January 19, 2026
- **Configuration:**
  - `torch_dtype`: bfloat16
  - `max_new_tokens`: 1000
  - `do_sample`: False (greedy decoding)

## Test Methodology
Simple zero-shot prompts asking MedGemma to generate discharge instructions across 5 common scenarios. No transformation guidance, reading level targets, or simplification instructions provided.

## Results

| Scenario | Prompt | Reading Level | Observation |
|----------|--------|---------------|-------------|
| Acetaminophen | "Generate patient discharge instructions for acetaminophen 500mg prescribed for post-surgical pain management." | 9.5 | Professional structure, comprehensive warnings |
| Hip Surgery | "Generate patient discharge instructions for hip replacement surgery recovery." | 9.6 | Detailed precautions, medical terminology |
| Diabetes Management | "Generate patient discharge instructions for Type 2 diabetes management including blood sugar monitoring, medication, diet, and foot care." | 10.2 | Most complex, extensive detail |
| Heart Failure | "Generate patient discharge instructions for congestive heart failure management including fluid restriction, daily weights, medications, and warning signs." | 9.7 | Technical medical language |
| Wound Care | "Generate patient discharge instructions for post-surgical wound care including dressing changes, infection signs, and activity restrictions." | 8.6 | Simplest of batch, still above target |

**Average Reading Level:** 9.5 grade  
**Range:** 8.6 - 10.2 grade

## Key Findings

### What MedGemma Does Well:
✅ Generates clinically accurate discharge instructions  
✅ Includes appropriate medical warnings  
✅ Structures information logically  
✅ Covers all relevant topics comprehensively  

### The Accessibility Gap:
❌ **Reading level 4-5 grades too high for 54% of Americans**  
❌ Uses medical terminology without simplification  
❌ Complex sentence structures (15-25 words average)  
❌ No audience-level differentiation

## Competitive Implications

**MedGemma's baseline capability confirms:**
1. The model CAN generate discharge instructions (not building new capability)
2. Output is clinically sound but **inaccessible** (9-10 grade level)
3. **Our value proposition:** Transform 9.5 grade → 4.5-5.5 grade while preserving medical accuracy

**This is NOT about:**
- Teaching MedGemma to generate discharge instructions (it already can)

**This IS about:**
- Health equity: Making medical information accessible to 54% of Americans
- Multi-audience transformation: Patient (4.5-5.5) vs Caregiver (6-7) vs Clinician (12+)
- Dignity-preserving simplification: Accessible without being condescending

## Next Steps
Test transformation system against these baseline examples to demonstrate:
- 4-5 grade level reduction
- Medical accuracy preservation
- Scalability across discharge types