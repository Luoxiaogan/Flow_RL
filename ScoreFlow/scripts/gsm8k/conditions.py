TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is the **GSM8K benchmark** (Grade School Math 8K). These are mathematical word problems designed at elementary school difficulty level.

**Core Characteristics:**
- **Input:** A word problem describing a real-world scenario with embedded numerical values and relationships
- **Required Skills:** Mathematical modeling, sequential calculation, unit tracking, and arithmetic operations
- **Answer Type:** Always a single numerical value (integer or decimal)

**Common Problem Types:**
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
- **Hidden Steps:** Some calculations require intermediate steps not explicitly stated
- **Order of Operations:** Must correctly sequence multiple calculations
- **Unit Consistency:** Keeping track of units (dollars, hours, items) throughout
- **Contextual Constraints:** Real-world constraints (can't have negative items, fractional people)

**Key Success Factors:**
- Clear identification of known values and unknowns
- Systematic step-by-step calculation with explicit intermediate results
- Verification that the answer makes sense in context
- Proper handling of units and decimal places
- Working through the problem chronologically when time-based

'''