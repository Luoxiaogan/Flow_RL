TASK_PROMPT = '''### Problem Domain Overview

This domain tests multi-step mathematical reasoning through word problems requiring 2-8 sequential calculations using basic arithmetic operations.

#### Key Characteristics & Requirements
- **Answer Format**: Single numerical value (integer or decimal)
- **Solution Steps**: 2-8 step reasoning chains using +, -, ×, ÷
- **Critical**: Track intermediate results and units throughout
- **Validation**: Final answer must be numerically exact
- **No Complex Math**: Only elementary arithmetic, no algebra or calculus

#### Common Problem Types & Solution Strategies
- **Sequential Operations**: Step-by-step calculations building on previous results
- **Rate Problems**: Distance/speed/time, work rates, unit prices
- **Distribution**: Dividing quantities, equal sharing, remainders
- **Proportions**: Percentages, fractions, ratios, scaling
- **Multi-entity**: Track different quantities for multiple people/objects

#### Workflow Focus Points
1. Extract all numerical values and their context
2. Identify what the question asks for
3. Build step-by-step calculation chain
4. Show intermediate results explicitly
5. Return final numerical answer only

#### Input Format
```
---
**QUESTION:**
[Complete word problem text]

'''