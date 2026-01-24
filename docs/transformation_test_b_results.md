# Test B‑v1: Dignity Optimization (Architecture B – Stage 2)

## Overview
Following completion of Tests A‑v1 through A‑v6, which focused exclusively on reading‑level transformation, Test B‑v1 evaluates the second major requirement of the system: **preserving patient dignity while maintaining accessibility**.

This test assesses whether the Stage 2 transformation (Architecture A) can apply dignity‑preserving language **without increasing reading level**, **without hallucinations**, and **without altering clinical meaning**.

**Testing Date:** January 21, 2026  
**Platform:** Kaggle GPU T4 x2  
**Pipeline:** Architecture B (Stage 1 → Stage 2)  
**Objective:** Evaluate dignity, tone, and respectfulness in transformed outputs.

---

## Purpose of Test B
While Test A focused on achieving a 4.5–5.5 grade reading level, Test B evaluates:

- **Respectful, adult‑appropriate tone**
- **Absence of condescending or infantilizing language**
- **Clear, direct phrasing without emotional manipulation**
- **Preservation of patient autonomy**
- **No unnecessary reassurance**
- **No fear‑based language**
- **No moralizing (“you must,” “you should have”)**
- **No diminutive phrasing (“just rest,” “don’t worry”)**

This test ensures the system supports the broader goal of **health literacy with dignity**, especially for patients who read below a 6th‑grade level.

---

## Test Strategy
Test B‑v1 evaluates the Stage 2 transformation using the **normalized outputs** from Stage 1 (Architecture B – Step 1). Each scenario is assessed for:

1. **Tone & Dignity**
   - Respectful, adult‑appropriate language  
   - No infantilizing or patronizing phrasing  

2. **Clinical Accuracy**
   - No loss of essential steps  
   - No added medical conditions  
   - No invented warnings  

3. **Reading Level Stability**
   - Target: 4.5–5.5  
   - No upward drift due to tone adjustments  

4. **Structural Integrity**
   - Three sections preserved  
   - No section drift  
   - No repetition  

5. **Hallucination Safety**
   - No invented symptoms  
   - No runaway lists  
   - No duplicated sections  

---

## Scenarios Tested
Same five discharge scenarios used in Test A:

1. Acetaminophen  
2. Hip Surgery  
3. Diabetes  
4. Heart Failure  
5. Wound Care  

This ensures comparability across architectures.

---

# Test B‑v1: Dignity Optimization (Architecture B – Stage 2)

## Results Summary

- **Average Reading Level:** *Not applicable for Stage 1* (Stage 1 does not simplify language; reading‑level evaluation begins in Stage 2)  
- **Success Rate (Dignity + Reading Level):** *0/5* (Stage 1 produced structural and content‑level hallucinations that prevent Stage 2 evaluation)  
- **Hallucinations:** *Severe and widespread* — duplication, runaway expansion, invented symptoms, and unbounded lists  
- **Tone Stability:** *Unstable* — tone drifted into clinical textbook style, bureaucratic phrasing, and in some cases overwhelming or fear‑inducing lists  
- **Clinical Accuracy:** *Compromised* — essential steps preserved, but large volumes of invented symptoms and irrelevant clinical content introduced  

---

## Detailed Results

### **Scenario 1: Acetaminophen**
| Metric | Result |
|--------|--------|
| Dignity | Mixed — tone remained neutral but became impersonal and generic |
| Reading Level | Not evaluated (Stage 1 only) |
| Clinical Accuracy | Partially preserved; however, entire sections were duplicated |
| Hallucinations | Yes — full duplication of all three sections |
| Notes | The model repeated the entire output twice, indicating structural instability and inability to normalize sparse content without hallucinating. |

---

### **Scenario 2: Hip Surgery**
| Metric | Result |
|--------|--------|
| Dignity | Poor — tone became overwhelming and fear‑inducing due to excessive warnings |
| Reading Level | Not evaluated |
| Clinical Accuracy | Severely compromised — dozens of invented symptoms and irrelevant clinical conditions |
| Hallucinations | Yes — runaway expansion loop producing 30+ “contact your provider” items |
| Notes | This scenario demonstrated the strongest inflation behavior, confirming that MedGemma cannot safely expand content density. |

---

### **Scenario 3: Diabetes**
| Metric | Result |
|--------|--------|
| Dignity | Poor — tone became alarmist due to repeated emergency warnings |
| Reading Level | Not evaluated |
| Clinical Accuracy | Compromised — repeated symptoms, invented conditions, and unbounded list growth |
| Hallucinations | Yes — repeated warning signs in a loop (similar to A‑v1 hallucination loop) |
| Notes | This scenario re‑exposed the repetition loop failure mode, confirming that density expansion triggers hallucinations. |

---

### **Scenario 4: Heart Failure**
| Metric | Result |
|--------|--------|
| Dignity | Acceptable — tone remained clinical and neutral |
| Reading Level | Not evaluated |
| Clinical Accuracy | Mostly preserved — no invented symptoms, but content remained dense |
| Hallucinations | Minimal — no runaway lists, but still added generic storage instructions |
| Notes | Heart Failure did not inflate, but also did not normalize; density remained high, confirming the model’s compression bias. |

---

### **Scenario 5: Wound Care**
| Metric | Result |
|--------|--------|
| Dignity | Acceptable — tone remained clinical and respectful |
| Reading Level | Not evaluated |
| Clinical Accuracy | Partially preserved — added generic medication instructions not present in original text |
| Hallucinations | Yes — invented medication‑related content and explanatory text |
| Notes | Model added new medication‑related content and explanatory sentences, violating the “no new clinical facts” rule. |

---

## Key Learnings

- **MedGemma cannot safely perform density normalization.**  
  Attempts to expand or compress content trigger hallucinations, duplication, and runaway lists.

- **Sparse scenarios inflate; dense scenarios remain dense.**  
  The model does not converge toward a medium‑density representation.

- **Hallucination risk increases when the model is asked to “expand,” “normalize,” or “add detail.”**  
  This mirrors the failure modes seen in A‑v1 and A‑v5.

- **Stage 1 must be deterministic, not generative.**  
  A rule‑based Python normalizer is required to standardize structure and density before applying Stage 2.

---

## Interpretation
Test B‑v1 provides the first evaluation of **tone and dignity** within the two‑stage pipeline. This test determines whether the system can:

- maintain accessibility  
- preserve clinical meaning  
- avoid condescension  
- avoid emotional manipulation  
- maintain structural integrity  

The results will guide refinement of Stage 2 and inform the design of **Hybrid Architecture C**, which balances readability, dignity, and clinical precision.

---

## Next Steps
1. Refine dignity‑preserving constraints based on Test B‑v1 findings  
2. Re‑run scenarios to validate improvements  
3. Begin development of **Hybrid Prompt (Test C)**  
4. Integrate findings into final competition documentation  

# Test B Series: Architecture B Testing Results

## Overview
Following Tests A-v1 through A-v6 (single-stage transformation), the Test B series evaluates **Architecture B: a two-stage pipeline** designed to normalize content density before applying reading-level transformation.

**Testing Period:** January 21-24, 2026  
**Platform:** Kaggle GPU T4 x2  
**Baseline Average:** 9.5 grade level (range: 8.6-10.2)  
**Target:** 4.5-5.5 grade level with preserved dignity and zero hallucinations  

---

## Test B-v2: Two-Stage Pipeline with Deterministic Normalizer
**Date:** January 21, 2026  
**Strategy:** Stage 1 (Python normalizer) → Stage 2 (MedGemma transformation)  
**Script:** `src/test_b_v2_content_normalizer.py`

### Architecture
```
Stage 1 (Deterministic): Parse clinical input → Structured format
Stage 2 (MedGemma): Structured input → Patient-level (4.5-5.5 grade)
```

### Results Summary
- **Execution:** Partial failure
- **Stage 1:** Functioned correctly (deterministic parsing)
- **Stage 2:** Severe hallucinations and failures

### Detailed Results
| Scenario | Stage 1 | Stage 2 Result | Issue |
|----------|---------|----------------|-------|
| Acetaminophen | ✓ Clean | HALLUCINATION | Massive drug interaction list loop |
| Hip Surgery | ✓ Clean | Acceptable | Verbose (6-8 grade estimate) |
| Diabetes | ✓ Clean | Wrong section | Emergency warnings misplaced |
| Heart Failure | ✓ Clean | Acceptable | Verbose (6-8 grade estimate) |
| Wound Care | ✓ Clean | EMPTY | No output generated |

### Critical Issues

**Acetaminophen Hallucination:**
```
Do not take this medication if you are taking warfarin.
Do not take this medication if you are taking phenobarbital.
[repeated 50+ medications in loop until token limit]
```
- Model invented comprehensive drug interaction list
- Content NOT present in Stage 1 input
- Clinically dangerous (overwhelming patient with irrelevant warnings)

**Wound Care Complete Failure:**
- Stage 2 produced empty output
- Model state corrupted by previous scenarios

### Key Learnings
- ✅ Stage 1 deterministic normalizer works correctly
- ❌ Stage 2 still hallucinates when given sparse input
- ❌ Batching 5 scenarios causes degradation across sequence
- **Hypothesis formed:** MedGemma may not be designed for batch processing

---

## Test B-v3 through B-v7: Single-Scenario Isolation Testing
**Date:** January 24, 2026  
**Strategy:** Test each scenario individually (restart kernel between tests)  
**Scripts:** `src/test_b_v3_single_scenario_isolation.py` through `test_b_v7_single_scenario_isolation.py`

### Hypothesis
MedGemma's discharge instruction capability was designed for ONE scenario at a time, not batch processing of multiple conditions simultaneously. Testing scenarios in isolation should eliminate context bleed and model state contamination.

### Test Methodology
Each scenario tested independently:
1. Fresh kernel restart
2. Load model once
3. Run single scenario through Stage 1 → Stage 2
4. Record results
5. Repeat for next scenario

### Complete Results
```
======================================================================
TEST B-v3 THROUGH B-v7 SUMMARY: ISOLATED SCENARIO TESTING
======================================================================
Scenario           | Baseline | Transformed | Reduction | Target  | Hallucinations
----------------------------------------------------------------------------------
Hip Surgery        | 9.6      | 4.8         | 4.8       | ✓ YES   | No
Wound Care         | 8.6      | 3.6         | 5.0       | ✗ NO    | No
Acetaminophen      | 9.5      | 5.8         | 3.7       | ✗ NO    | Yes
Heart Failure      | 9.7      | 3.5         | 6.2       | ✗ NO    | No
Diabetes           | 10.2     | 5.1         | 5.1       | ✓ YES   | Yes
----------------------------------------------------------------------------------
AVERAGE            | 9.5      | 4.6         | 4.9       | 2/5     | 2/5
======================================================================
```

---

## Detailed Scenario Analysis

### Test B-v3: Hip Surgery ✓ SUCCESS
**Reading Level:** 4.8 (target: 4.5-5.5)  
**Status:** ✓ Target met  
**Hallucinations:** None

**Output Quality:**
```
MEDICATION: Take Rivaroxaban as directed. Follow your doctor's instructions...

WHAT TO DO / WHAT NOT TO DO:
- Keep your hip protected. Avoid bending your hip more than 90 degrees.
- Do not let your leg touch the side of bed.
- Keep your incision clean and dry.

CALL DOCTOR RIGHT AWAY IF:
- You see redness or pus near your incision.
- Your incision opens up or looks worse.
- You feel sudden pain or swelling in your leg.
```

**Analysis:**
- ✅ Clear, simple language
- ✅ 8-12 word sentences
- ✅ Adult-appropriate tone
- ✅ No medical jargon
- ✅ Preserves all critical clinical information
- **This is the ONLY scenario to fully meet all requirements**

---

### Test B-v4: Wound Care ✗ TOO LOW
**Reading Level:** 3.6 (target: 4.5-5.5)  
**Status:** ✗ Below target range  
**Hallucinations:** None

**Output Quality:**
```
WHAT TO DO / WHAT NOT TO DO:
- Change your dressing daily.          (4 words)
- Pat your wound dry gently.            (5 words)
- Keep your wound clean and dry.        (6 words)
```

**Analysis:**
- ✅ Clinically accurate
- ✅ No hallucinations
- ✅ Clear instructions
- ❌ Sentences TOO SHORT (4-6 words vs target 8-15)
- **Root cause:** MedGemma over-compresses simple scenarios

---

### Test B-v5: Acetaminophen ✗ TOO HIGH + HALLUCINATIONS
**Reading Level:** 5.8 (target: 4.5-5.5)  
**Status:** ✗ Above target range  
**Hallucinations:** Yes - invented emergency warnings

**Hallucinated Content:**
```
WHAT TO DO / WHAT NOT TO DO:
- Rest your body.                    ← NOT in input
- Drink plenty of fluids.            ← NOT in input
- Avoid driving or operating...      ← NOT in input

CALL DOCTOR IF:
- You have trouble breathing.        ← NOT in input
- You feel dizzy or lightheaded.    ← NOT in input
- You have severe headache.          ← NOT in input
- You have chest pain.               ← NOT in input
- You have confusion...              ← NOT in input
```

**Analysis:**
- ❌ Stage 1 output was sparse (medication-only)
- ❌ Stage 2 filled structural gaps with generic medical advice
- ❌ Clinically dangerous (invented warnings)
- **Root cause:** Deterministic normalizer too simplistic for medication-only scenarios

---

### Test B-v6: Heart Failure ✗ TOO LOW
**Reading Level:** 3.5 (target: 4.5-5.5)  
**Status:** ✗ Below target range  
**Hallucinations:** None

**Output Quality:**
```
Take furosemide 40mg daily as prescribed.     (6 words)
Take carvedilol 6.25mg twice a day...         (7 words)
Weigh yourself daily at same time.            (6 words)
```

**Analysis:**
- ✅ Clinically accurate (all medications preserved)
- ✅ No hallucinations
- ❌ Sentences too short (4-8 words)
- **Same compression pattern as Wound Care**

---

### Test B-v7: Diabetes ✓ BARELY IN TARGET + HALLUCINATIONS
**Reading Level:** 5.1 (target: 4.5-5.5)  
**Status:** ✓ Technically meets target (by 0.1 grade)  
**Hallucinations:** Yes - invented emergency warnings

**Hallucinated Content:**
```
CALL DOCTOR IF:
- You have chest pain.                ← NOT in input
- You have sudden shortness...        ← NOT in input
- You have severe headache.           ← NOT in input
- You have sudden vision changes.     ← NOT in input (though relevant to diabetes)
- You have signs of infection...      ← NOT in input
```

**Analysis:**
- ✅ Reading level barely in target
- ✅ Medication instructions preserved
- ❌ Invented emergency warnings (Stage 1 only said "Monitor for concerning symptoms")
- **Root cause:** Vague Stage 1 placeholder forced Stage 2 to hallucinate specifics

---

## Systematic Pattern Analysis

### What Isolation Testing Proved

**✅ Hypothesis VALIDATED:**
- No cross-scenario contamination when testing individually
- No infinite repetition loops (diabetes loop from A-v1 eliminated)
- More predictable behavior per scenario

**❌ New Pattern REVEALED:**

| Input Complexity | Result | Reading Level | Pattern |
|------------------|--------|---------------|---------|
| **High** (Hip Surgery, Diabetes) | ✓ | 4.8-5.1 | Works when rich input |
| **Medium** (Heart Failure) | ✗ | 3.5 | Over-compressed |
| **Low** (Wound Care) | ✗ | 3.6 | Over-compressed |
| **Low + Sparse** (Acetaminophen) | ✗ | 5.8 + hallucinate | Fills structural gaps |

### MedGemma's Sentence Compression Bias

**Observed behavior:**
- Rich, complex inputs → MedGemma produces 8-12 word sentences → Target met
- Simple inputs → MedGemma produces 4-6 word sentences → Below target
- Sparse inputs → MedGemma invents content to fill structure → Hallucinations

**Conclusion:** MedGemma has internal heuristics that adjust sentence length based on perceived content density, which cannot be overridden by prompt instructions alone.

---

## Root Cause: Stage 1 Normalizer Limitations

### The Deterministic Normalizer Code:
```python
def normalize_content(clinical_input):
    normalized = {
        "medication": [],
        "care_instructions": [],
        "urgent_signs": []
    }
    # Simplistic parsing
    output = "**MEDICATION**\n"
    output += clinical_input  # Dumps everything
    output += "\n\n**CARE INSTRUCTIONS**\n"
    output += clinical_input  # Duplicates content
    output += "\n\n**URGENT WARNING SIGNS**\n"
    output += "Monitor for concerning symptoms."  # Generic placeholder
    return output
```

### Problems Identified:

1. **Content Duplication**
   - Medication section duplicated into care instructions
   - Creates redundancy that confuses Stage 2

2. **No Actual Parsing**
   - Doesn't extract specific medications, instructions, or warnings
   - Just dumps entire input into each section

3. **Generic Placeholders**
   - "Monitor for concerning symptoms" is too vague
   - Forces Stage 2 to invent specific warnings (hallucinations)

4. **No Density Adjustment**
   - Doesn't expand sparse scenarios
   - Doesn't compress verbose scenarios
   - Passes problems downstream to Stage 2

---

## Strategic Implications

### What We Successfully Demonstrated

✅ **Reading level reduction is possible** (9.5 → 4.6 average)  
✅ **Target is achievable** (Hip Surgery: 4.8, Diabetes: 5.1)  
✅ **Isolation prevents cross-contamination** (no batch degradation)  
✅ **Systematic testing methodology** (controlled iteration)  
✅ **Root cause identification** (Stage 1 normalizer, sentence compression bias)  

### Remaining Technical Challenges

⚠️ **Consistency:** Only 2/5 scenarios hit target (40% success rate)  
⚠️ **Hallucination prevention:** 2/5 scenarios invented content  
⚠️ **Sentence length control:** MedGemma compresses simple scenarios too aggressively  
⚠️ **Stage 1 normalizer:** Requires complete redesign for production use  

## Lessons Learned

### Architecture Insights

1. **Single-stage transformation insufficient**
   - Tests A-v1 through A-v6 proved prompt-only approach hits limits
   - Two-stage pipeline required for consistent results

2. **Isolation matters**
   - Batch processing causes model state contamination
   - Individual scenario processing required for reliable behavior

3. **Stage 1 must be deterministic**
   - Generative normalization triggers hallucinations
   - Rule-based Python parser needed (not LLM-based)

4. **MedGemma has internal heuristics**
   - Sentence length adjusts based on input density
   - Cannot be fully controlled by prompt instructions
   - Must work WITH model behavior, not against it
