# Prompt Evolution Analysis

## Overview
Analysis of 8 prompts across 4 test runs to identify what works for consistent 4.5-5.5 grade output.

---

## Prompt Comparison Table

| Element | Run 1 | Run 2 | Run 3 (Best) | Run 4 | Universal (Proposed) |
|---------|-------|-------|--------------|-------|----------------------|
| **Approach** | Comprehensive | Detailed | Minimalist | Dignity-preserving | Universal |
| **Section limit** | None | None | 3-4 / 4-6 | 3-4 / 4-6 | 4-6 adaptive |
| **Sentence length** | None specified | None specified | 5-10 words | 8-12 words | 8-12 words variety |
| **Grade target** | 4-5 (vague) | 4-5 (vague) | 4th grade | 4.5-5.5 explicit | 4.5-5.5 explicit |
| **Exclusions** | None | None | ✓ Explicit list | ✓ Explicit list | ✓ Explicit list |
| **Red flag only** | No | No | ✓ Yes | ✓ Yes | ✓ Yes |
| **Examples in prompt** | No | No | No | ✓ Good/bad examples | ✓ Good/bad examples |
| **Real-world context** | No | No | No | ✓ Encouraged | ✓ Encouraged |
| **Acetaminophen result** | 6.4 | 8.4 | **4.9 ✓** | 5.6 | TBD |
| **Hip surgery result** | 5.4 | 6.0 | 3.0 | **4.0 ✓** | TBD |

---

## What Worked (Keep These)

### ✅ From Run 3 (Red Flag Framework):
- **Hard section limits** (3-4 or 4-6 sections max)
- **Red flag warnings only** (life-threatening info only)
- **Explicit exclusion lists** (what NOT to include)
- **Structural templates** (exact section names)
- **Observable symptoms only** (yellow skin, not jaundice)

### ✅ From Run 4 (Dignity-Preserving):
- **Sentence variety guidance** (8-12 words, with range)
- **Real-world examples** (like sitting in a low chair)
- **Good/bad examples in prompt** (shows model what to aim for)
- **Explicit grade target** (4.5-5.5, not just "4-5")
- **Dignity language** ("accessible but dignified")

---

## What Didn't Work (Avoid These)

### ❌ From Run 1-2 (Comprehensive Approach):
- **Open-ended requests** ("add safety limits" → model adds EVERYTHING)
- **No exclusions** (model includes allergy warnings, pregnancy, etc.)
- **Vague targets** ("4-5 grade" without enforcement)
- **No sentence limits** (allows verbose output)

### ❌ From Run 3 (Over-Minimalist):
- **Too-short sentences** (5-10 words → 3-7 actual → 3.0 grade)
- **No variety guidance** (all sentences same length = choppy)
- **No context examples** (missed "like sitting in low chair")

### ❌ From Run 4 (Structure Issues):
- **Repetitive sentence patterns** ("Call your doctor right away if..." × 3)
- **Condition-specific prompts** (doesn't scale)
- **No automatic section detection** (manual specification needed)

---

## Winning Formula for Universal Prompt

### Core Elements:
1. **Section adaptability** - Auto-detect relevant sections from input
2. **Sentence variety** - 8-12 words average, with natural range (6-15)
3. **Red flag only** - Life-threatening or hospitalization-risk info
4. **Explicit exclusions** - Clear list of what to omit
5. **Grade target** - 4.5-5.5 explicitly stated
6. **Context examples** - Encourage parenthetical real-world examples
7. **Good/bad examples** - Show desired sentence patterns
8. **Universal medication naming** - Rules that work for any drug
9. **Observable language** - Concrete symptoms, not medical terms
10. **Dignity-preserving tone** - Respectful, adult language

### Test Run 5 Goal:
Validate that ONE prompt produces consistent 4.5-5.5 output across:
- Medications (acetaminophen)
- Procedures (hip surgery)
- Future: Chronic conditions, wound care, any discharge type