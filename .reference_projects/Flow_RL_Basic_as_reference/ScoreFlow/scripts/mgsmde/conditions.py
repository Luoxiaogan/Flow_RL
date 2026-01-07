TASK_PROMPT = '''### Problem Domain Overview

MGSM German (Multilingual Grade School Math - German) tests mathematical word problem solving in German language at elementary school level.

#### Key Characteristics & Requirements
- **Input:** A word problem in German describing a real-world scenario with embedded numerical values and relationships
- **Required Skills:** Mathematical modeling, sequential calculation, unit tracking, and arithmetic operations
- **Language:** German (Deutsch) - problems are presented in German language
- **Answer Type:** Always a single numerical value (integer or decimal)

#### Common Problem Types & Solution Strategies
- **Sequential Operations:** Multiple steps that build on each other (deposit then withdrawal)
- **Rate Problems:** Distance/speed/time, work rates, unit prices
- **Proportional Reasoning:** Ratios, percentages, fractions, scaling
- **Distribution Problems:** Dividing quantities, equal sharing, remainders
- **Comparison Problems:** Finding differences, determining "how many more"
- **Multi-entity Tracking:** Problems involving multiple people/objects with different quantities

**Mathematical Operations:**
- Basic arithmetic: addition, subtraction, multiplication, division
- Fractions and decimals
- Percentages and proportions
- Simple algebra (solving for unknowns)
- Unit conversions

**Critical Challenges:**
- **Language Processing:** Understanding German mathematical terminology and phrasing
- **Hidden Steps:** Some calculations require intermediate steps not explicitly stated
- **Order of Operations:** Must correctly sequence multiple calculations
- **Unit Consistency:** Keeping track of units throughout (Euro, Stunden, Artikel)
- **Contextual Constraints:** Real-world constraints (can't have negative items, fractional people)


#### Workflow Focus Points
1. Clear identification of known values and unknowns from German text
2. Systematic step-by-step calculation with explicit intermediate results
3. Verification that the answer makes sense in context
4. Proper handling of units and decimal places
5. Working through the problem chronologically when time-based

#### Input Format
```
---
**PROBLEM:**
[Word problem in target language with numerical values and relationships]
---
```
Multiple problems follow the same structure if provided.'''