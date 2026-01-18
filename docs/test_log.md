# MedGemma Test Log

## Purpose
Track test runs, prompt refinements, and output quality progression.

---

## Test Run 1: Baseline
**Date:** January 16, 2026  
**Time:** ~10:00 AM  
**Configuration:** 
- `max_new_tokens`: 200
- `dtype`: bfloat16
- `device`: CPU

### Prompt Strategy
**Comprehensive detail approach:**
- "Add concrete safety limits"
- "Explain consequences in plain terms"
- "Create sections with headers"
- Multiple structural requirements

### Results

**Acetaminophen:**
- Readability: **6.4 grade level** ✗ (above target)
- Brand naming: Failed (used "acetaminophen" not "Tylenol")
- Safety info: Good (added max daily dose)
- Structure: Well-organized but verbose

**Hip Surgery:**
- Readability: **5.4 grade level** ⚠️ (close to target)
- Completeness: **Truncated** (hit 200 token limit mid-sentence)
- Structure: Excellent (empowering title, DO/DON'T format)
- Tone: Patient-centered and clear

### Key Observations
- Model understood transformation task
- Detailed prompts produced organized output BUT higher reading levels
- Token limit too low for complex instructions
- Brand naming directive not strong enough

### Decisions Made
1. Increase `max_new_tokens` to allow full hip surgery output
2. Refine brand naming to dual-format: "generic (Brand or store brand)"
3. Test if more detailed prompts improve or worsen readability

---

## Test Run 2: Token & Naming Refinement
**Date:** January 17, 2026  
**Time:** ~10:30 AM  
**Configuration:**
- `max_new_tokens`: 200 → 1200
- `dtype`: bfloat16
- `device`: CPU

### Changes Made
- Increased tokens to allow complete hip surgery output
- Updated brand naming instruction: "generic (Brand or store brand)"
- Kept comprehensive prompt structure

### Prompt Strategy
**Same detailed approach as Run 1:**
- Target 4th-5th grade
- Replace abbreviations
- Use dual brand naming format
- Add safety limits
- Explain consequences
- Create structured sections

### Results

**Acetaminophen:**
- Readability: **8.4 grade level** ✗✗ (WORSE than Run 1)
- Brand naming: Still failed (used "Pain Medicine" not "acetaminophen (Tylenol)")
- Output quality: Over-engineered
- Problem: Added extensive contraindications list, meta-commentary section

**Hip Surgery:**
- Readability: **6.0 grade level** ⚠️ (slightly above target)
- Completeness: ✅ Full output achieved
- Structure: Excellent (all sections present)
- Problem: Added "Getting Started at Home" and "Why These Rules" sections (increased complexity)

### Critical Discovery
**Counterintuitive finding:** MORE detailed prompts = HIGHER reading levels

**Why:**
- Prompt requested comprehensive information
- Model interpreted this as "add everything I know"
- Added: allergy warnings, pregnancy warnings, environmental advice, "why" explanations
- Result: Longer, more complex output

**Acetaminophen trend:** 6.4 → 8.4 (moving WRONG direction)

### Decisions Made
1. Shift strategy: Minimalist prompts, not detailed prompts
2. Implement "red flag framework" (critical warnings only)
3. Add explicit exclusion lists (what NOT to include)
4. Set hard sentence length limits (5-10 words)
5. Set hard section limits (3-4 for meds, 4-6 for surgery)

### Key Insight
> "Initial testing revealed a counterintuitive finding: detailed, comprehensive prompts produced outputs with HIGHER reading levels. Minimalist prompts focusing on core simplification produced better health literacy outcomes."

---

## Test Run 3: Red Flag Framework ✅ SUCCESS
**Date:** January 17, 2026  
**Time:** ~1:00 PM  
**Configuration:**
- `max_new_tokens`: 1000 (optimized from 1200)
- `dtype`: bfloat16 (fixed deprecation)
- `device`: CPU

### Changes Made
**Complete prompt redesign:**
- Minimalist approach (3-6 sections max)
- Explicit sentence length limits (5-10 words, max 15)
- Red flag only framework (life-threatening warnings only)
- Explicit exclusion lists
- Structural templates (told model EXACTLY which sections to create)

### Red Flag Framework
**🔴 Critical (Always Include):**
- Drug interactions causing immediate harm (alcohol + acetaminophen)
- Overdose limits (maximum daily dose)
- Emergency symptoms (yellow skin, dark urine, chest pain)
- Hip dislocation movements
- Infection signs requiring immediate action

**🟡 General (Exclude from Patient Level):**
- Allergy warnings (patients already know)
- Pregnancy precautions (contextual)
- Environmental setup (rugs, lighting)
- "Why" explanations
- Reassurance statements

### Updated Prompts

**Acetaminophen Prompt (v3):**
```
You are a patient communication specialist. Transform these clinical medication instructions into essential guidance patients can act on.

CRITICAL REQUIREMENTS:
- Write 3-4 short sections maximum
- Use extremely short sentences (5-10 words each)
- Target 4th grade reading level
- Focus ONLY on critical actions and red flag warnings

STRUCTURE (Use These Exact Sections):
1. MEDICATION: [name in dual format]
2. HOW TO TAKE: 2-3 sentences max
3. IMPORTANT SAFETY: Red flags only
4. CALL DOCTOR IF YOU SEE: Observable symptoms

EXCLUDE:
- General side effects
- Allergy warnings
- Pregnancy precautions
- "Why" explanations

RED FLAG WARNINGS ONLY:
- Alcohol interaction
- Overdose limits
- Emergency symptoms

Keep every sentence under 15 words. Use common words only.
```

**Hip Surgery Prompt (v3):**
```
You are a patient communication specialist. Transform these clinical discharge instructions into essential guidance patients can act on.

CRITICAL REQUIREMENTS:
- Write 4-6 short sections maximum
- Use extremely short sentences (5-10 words each)
- Target 4th grade reading level
- Focus ONLY on critical actions and red flag warnings

STRUCTURE (Use These Exact Sections):
1. MEDICATIONS
2. WHAT NOT TO DO WITH YOUR HIP
3. WATCH YOUR WOUND
4. CALL DOCTOR RIGHT AWAY IF
5. FOLLOW-UP

EXCLUDE:
- "Getting started at home" information
- "Why these rules matter" explanations
- Reassurance statements
- Environmental setup advice
- Repetition

RED FLAG WARNINGS ONLY:
- Hip dislocation movements
- Blood clot medication (critical)
- No NSAIDs (bleeding risk)
- Infection/emergency signs

MEDICATION NAMING:
- Rivaroxaban: "blood thinner medicine"
- Oxycodone: "pain medicine"

Keep every sentence under 15 words. Use common words only.
```

### Results ✅ BREAKTHROUGH

**Acetaminophen:**
- Readability: **4.9 grade level** ✅ TARGET ACHIEVED
- Improvement: **11.7 grade levels** (16.6 → 4.9)
- Sections: 4 (Medication, How to Take, Important Safety, Call Doctor)
- Sentence length: 5-10 words per sentence
- Brand naming: Still needs refinement (used "Acetaminophen" not dual format)
- Safety: Alcohol warning, overdose limit, liver damage signs ✓

**Output sample:**
```
MEDICATION: Acetaminophen

HOW TO TAKE:
Take 500mg pills with water.
Take one pill every 6 hours.
Take more pills only if needed for pain.

IMPORTANT SAFETY:
Do not take more than 3000mg in 24 hours.
Taking too much can damage your liver.
Do not drink alcohol while taking this medicine.

CALL DOCTOR IF YOU SEE:
Yellow skin or eyes.
Dark urine.
Severe stomach pain.
Signs of liver problems.
```

**Hip Surgery:**
- Readability: **3.0 grade level** ✅✅ EXCEEDED TARGET
- Improvement: **12.0 grade levels** (15.0 → 3.0)
- Sections: 5 (Medications, Hip Precautions, Wound, Emergency, Follow-up)
- Sentence length: 3-7 words per sentence (ultra-concise)
- Content: Red flags only, no fluff
- Emergency criteria: Chest pain, bleeding, numbness, fever ✓

**Output sample:**
```
MEDICATIONS
Take your blood thinner medicine.
Take it every day.
Don't take ibuprofen or Advil.

WHAT NOT TO DO WITH YOUR HIP
Don't bend your hip past 90 degrees.
Don't move your hip past the middle line.
Don't turn your hip inward.
Use your walker.

CALL DOCTOR RIGHT AWAY IF
Chest pain occurs.
Severe bleeding happens.
Numbness occurs.
Fever is present.
```

### Comparison: Run 2 vs Run 3

| Metric | Run 2 (Detailed) | Run 3 (Red Flag) | Change |
|--------|------------------|------------------|--------|
| **Acetaminophen Grade** | 8.4 | 4.9 | ⬇️ 3.5 grades |
| **Hip Surgery Grade** | 6.0 | 3.0 | ⬇️ 3.0 grades |
| **Acetaminophen Target** | ✗ Failed | ✅ Achieved | **SUCCESS** |
| **Hip Surgery Target** | ⚠️ Close | ✅ Exceeded | **SUCCESS** |

### Key Success Factors

**What Made This Work:**
1. **Section limits** - Hard caps on number of sections
2. **Sentence constraints** - Explicit word count limits
3. **Exclusion lists** - Told model what NOT to include
4. **Red flag only** - Limited to life-threatening information
5. **Structural templates** - Exact section names provided
6. **Observable language** - "Yellow skin" not "jaundice"

### Remaining Issues
1. **Brand naming:** Still not using "acetaminophen (Tylenol or store brand)" format
2. **Minor refinement:** May need to strengthen dual-naming directive

### Strategic Implications

**For Competition:**
- Proven methodology for achieving 4-5th grade reading level
- Red flag framework = sophisticated health literacy design
- Demonstrates iterative refinement process
- Shows data-driven decision making

**For Multi-Audience System:**
- Patient level: Red flags only (3.0-4.9 grade) ✅ Proven
- Caregiver level: Red + yellow flags (6-7 grade) - Next to build
- Clinician level: Complete detail (12+ grade) - Next to build

### Next Steps
1. Fix brand naming directive (minor refinement)
2. Build caregiver-level prompt (moderate detail, 6-7 grade target)
3. Build clinician-level prompt (professional reorganization)
4. Create comparison interface showing all three levels
5. Test with additional discharge examples
6. Document methodology for competition writeup

---

## Summary Stats

| Test Run | Acetaminophen Grade | Hip Surgery Grade | Status |
|----------|---------------------|-------------------|--------|
| Run 1 (Baseline) | 6.4 | 5.4 (truncated) | ⚠️ Close |
| Run 2 (Detailed) | 8.4 | 6.0 | ✗ Worse |
| Run 3 (Red Flag) | **4.9** | **3.0** | ✅ **SUCCESS** |

**Target:** 4-5th grade reading level  
**Achieved:** 4.9 (acetaminophen), 3.0 (hip surgery)  
**Methodology:** Red flag framework + minimalist prompts + explicit constraints

---

**Status:** Patient-level transformation PROVEN ✅  
**Next:** Build caregiver and clinician levels

## Test Run 4: Dignity-Preserving Consistency
**Date:** January 17, 2026  
**Time:** ~2:30 PM  
**Configuration:**
- `max_new_tokens`: 1000
- `dtype`: bfloat16
- `device`: CPU

### Changes Made
**Goal:** Raise hip surgery from 3.0 to 4.5-5.5 while maintaining acetaminophen at ~4.9

**Prompt adjustments:**
- Sentence length: "5-10 words" → "8-12 words with variety"
- Added explicit variety instruction
- Encouraged real-world examples in parentheses
- Explicit target: "4.5-5.5 grade reading level (accessible but dignified)"
- Provided good vs. bad sentence examples

### Results

**Acetaminophen:**
- Readability: **5.6 grade level** ⚠️ (slightly above target)
- vs Run 3: 4.9 → 5.6 (regressed 0.7 grades)
- Issue: Repetitive "Call your doctor right away if..." structure increased complexity
- Brand naming: Still missing dual format

**Hip Surgery:**
- Readability: **4.0 grade level** ✓ (within target range)
- vs Run 3: 3.0 → 4.0 (improved 1.0 grade - SUCCESS)
- Dignity: Much better - added real-world examples
- Tone: More natural, adult, respectful

**Output sample (Hip Surgery improvement):**
```
Don't bend your hip past 90 degrees. This is like sitting in a low chair.
Don't cross your legs.
Don't twist your hip inward.
```

### Key Observations

**What worked:**
- Real-world examples improved clarity without increasing complexity
- Sentence variety guidance helped hip surgery feel more natural
- 4.0 is better than 3.0 for dignity while still highly accessible

**What didn't work:**
- Acetaminophen regressed (5.6 vs 4.9)
- Repetitive sentence structures increased grade level
- Still using condition-specific prompts (scalability issue)

### Critical Insight: Scalability Problem Identified

**Current approach:**
- Separate prompt for medications
- Separate prompt for procedures
- Would need separate prompts for diabetes, heart failure, wound care, etc.

**This doesn't scale to production.**

**Need:** ONE universal patient-level prompt that works for ANY discharge scenario

### Decisions Made
1. **Strategic pivot:** Abandon condition-specific prompts
2. **Build universal prompt:** Single framework for all discharge types
3. **Test Run 5:** Validate universal prompt on multiple examples
4. **Consistency validation:** Prove 4.5-5.5 grade across different scenarios

---

## Test Runs 1-4: Summary Comparison

### Readability Progression

| Test Run | Acetaminophen | Hip Surgery | Strategy |
|----------|---------------|-------------|----------|
| Run 1 | 6.4 | 5.4 (truncated) | Comprehensive detail |
| Run 2 | 8.4 ⬆️ | 6.0 ⬆️ | More detail (worse) |
| Run 3 | 4.9 ✓ | 3.0 ⚠️ | Red flag + minimalist |
| Run 4 | 5.6 ⚠️ | 4.0 ✓ | Dignity-preserving |

### Key Learnings Across All Runs

**1. More detail ≠ better readability**
- Run 2 proved detailed prompts produce HIGHER grade levels
- Comprehensive safety info increased complexity unnecessarily

**2. Extreme simplicity (3.0 grade) feels elementary**
- Run 3 hip surgery was too choppy
- Lacked dignity and natural flow

**3. Sweet spot: 4.5-5.5 grade level**
- Accessible to 80% of Americans
- Maintains adult, respectful tone
- Room for helpful context

**4. Sentence structure matters more than word choice**
- Repetitive structures increase complexity
- Variety in length improves natural flow
- Real-world examples help without increasing grade level

**5. Condition-specific prompts don't scale**
- Need universal framework
- Consistency across all discharge types critical

### Next: Universal Prompt Framework (Test Run 5)