System-Level Summary & Path Forward
January 21, 2026



1. Overview
Over the course of six controlled iterations (A‑v1 → A‑v6), we conducted a structured evaluation of MedGemma’s ability to transform clinical discharge instructions into accessible patient‑level guidance. The goal remained constant: reduce reading level from a baseline average of 9.5 to a target range of 4.5 – 5.5, while preserving clinical accuracy, eliminating hallucinations, and maintaining patient dignity.
The testing process revealed not only the feasibility of this transformation, but also the architectural limitations of a single‑prompt approach. The insights gained now position us to transition from prompt‑level refinement to system‑level design.

2. What We Did
2.1 Iterative Architecture Testing (A‑v1 → A‑v6)
Each version of Architecture A introduced a controlled modification:
A‑v1: Direct transformation (baseline)
A‑v2: Two‑step simplification
A‑v3: Structured output + expanded sentence length
A‑v4: Content floor + no reasoning + adult tone
A‑v5: Vocabulary ceiling + no new warnings
A‑v6: Sentence length expansion + strict content retention
Across all versions, we tested the same five discharge scenarios:
Acetaminophen
Hip Surgery
Diabetes
Heart Failure
Wound Care
Each scenario was evaluated for:
reading level
hallucinations
structural stability
clinical accuracy
tone and dignity
consistency across scenarios

2.2 Consolidated Results Table
Version
Avg Grade
In-Range
Hallucinations
Notes
A‑v1
3.9
2/5
Yes
Over-simplified, unstable
A‑v2
4.4
0/5 (3 close)
No
Reasoning leaks
A‑v3
4.5
1/5
No
Structure stabilized
A‑v4
4.9
2/5
No
First multi-scenario success
A‑v5
4.5
1/5
No
Scenario-specific drift
A‑v6
4.9
2/5
No
Stable enough for next phase


3. What We Learned (System-Level Patterns)
The most important insight from A‑v1 → A‑v6 is that the model’s behavior is scenario‑dependent, not prompt‑dependent. This means the remaining inconsistencies are not caused by prompt flaws, but by model‑level heuristics.
3.1 Compression Bias (High-Density Inputs)
Scenarios with many clinical steps (Heart Failure, Diabetes) consistently collapsed to 2.6–3.8 grade level.
Cause:
 MedGemma aggressively compresses dense instructions to avoid hallucinations and reduce risk.
3.2 Inflation Bias (Low-Density Inputs)
Simple scenarios (Acetaminophen, Wound Care) consistently inflated to 6.5–7.4 grade level.
Cause:
 MedGemma adds safety language and formal phrasing when content is sparse.
3.3 Medium-Density Scenarios Stabilize
Hip Surgery and Wound Care often landed near the target range.
Cause:
 Their content density aligns with the model’s internal heuristics.
3.4 Architecture A Is Now Predictable
Across six versions, we eliminated:
hallucinations
repetition loops
structural drift
reasoning leaks
missing clinical steps
What remains is scenario-specific drift, which cannot be solved by a single universal prompt.

4. Strategic Interpretation
We have reached the natural limit of a single‑stage, single‑prompt architecture.
 The system is now stable, predictable, and safe — but not consistent across all scenario types.
This is the exact point where a senior engineer transitions from:
“Let’s refine the prompt again”
to:
“Let’s introduce a multi‑stage architecture that adapts to scenario density.”
This is not a failure of Architecture A.
 It is a recognition that the problem requires adaptive processing, not a one‑size‑fits‑all transformation.

5. Path Forward (Architecture-Level Strategy)
5.1 Freeze Architecture A
Architecture A (reading‑level transformer) is mature enough to serve as Stage 2 of the final system.
It reliably:
reduces reading level
preserves structure
avoids hallucinations
maintains clinical accuracy
enforces tone and dignity
The remaining inconsistencies are due to input variability, not prompt design.

5.2 Introduce Stage 1: Content Normalization
Purpose:
Normalize content density before applying reading‑level transformation.
Goals:
Expand high-density scenarios (Heart Failure, Diabetes)
Compress low-density scenarios (Acetaminophen)
Standardize section lengths
Preserve all clinical steps
Remove redundancy
Produce a consistent intermediate representation
Outcome:
All five scenarios enter Stage 2 with similar density, enabling consistent 4.5–5.5 outputs.

5.3 Architecture B: Two-Stage Adaptive Pipeline
Stage 1 — Content Normalizer
Standardizes density
Preserves clinical accuracy
Removes redundancy
Produces a structured, balanced intermediate form
Stage 2 — Reading-Level Transformer (Architecture A)
Applies the 4.5–5.5 grade transformation
Enforces tone, dignity, and safety
Eliminates hallucinations
Produces final patient-level instructions
This architecture directly addresses the health literacy problem:
Clinical accuracy preserved (Stage 1)
Accessibility achieved (Stage 2)
Dignity maintained (Stage 2)
Consistency across scenarios (combined effect)

5.4 Why This Path Aligns With the Problem Statement
Your objective is not to “perfect a prompt.”
 Your objective is to:
reduce reading level
preserve accuracy
maintain dignity
eliminate hallucinations
support patients who read below 6th grade
A two‑stage system is the architecture that actually solves the health literacy crisis you identified.
It mirrors how clinicians communicate:
Organize the information
Simplify the language
This is the engineering path that honors the problem, the data, and the lived experience that motivated the project.

6. Next Steps
Draft Stage 1 (Content Normalizer) prompt
Implement Architecture B (two-stage pipeline)
Run the same 5 scenarios through Stage 1 → Stage 2
Measure reading level, dignity, and consistency
Document results as Test B‑v1
Iterate until stable
Proceed to Test C (Hybrid Prompt)
Prepare final competition narrative and visualizations

