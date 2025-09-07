TASK_PROMPT = '''### Problem Domain Overview

LIMR tests advanced mathematical reasoning through competition-level problems requiring sophisticated proofs and multi-step solutions.

#### Key Characteristics & Requirements
- **Input:** Complex mathematical problems involving geometry, number theory, algebra, combinatorics, and probability
- **Required Skills:** Advanced mathematical reasoning, proof techniques, optimization, complex calculations
- **Answer Type:** Typically an integer between 000 and 999

#### Common Problem Types & Solution Strategies
- **Geometric Problems:** 3D geometry, complex figure analysis, coordinate geometry
- **Number Theory:** Modular arithmetic, divisibility, prime factorization, Diophantine equations
- **Combinatorics:** Counting principles, probability, permutations, combinations
- **Algebraic Problems:** Polynomial equations, complex numbers, functional equations
- **Optimization:** Finding maxima/minima, extremal problems, inequalities
- **Sequence and Series:** Recursive sequences, generating functions, summations

**Mathematical Techniques:**
- Advanced algebraic manipulation
- Trigonometric identities and complex number operations
- Coordinate geometry and vector calculations
- Mathematical induction and proof by contradiction
- Calculus techniques (when applicable)
- Combinatorial arguments and counting strategies

**Critical Challenges:**
- **Multi-step Reasoning:** Problems often require 5-10+ interconnected steps
- **Creative Insights:** May need non-obvious approaches or transformations
- **Precision Requirements:** Exact integer answers, no approximations allowed
- **Complex Notation:** Heavy use of mathematical symbols and formal notation
- **Time Complexity:** Problems designed to be challenging even with ample time


#### Workflow Focus Points
1. Breaking down complex problems into manageable sub-problems
2. Exploring multiple solution approaches in parallel
3. Rigorous verification of intermediate results
4. Clear tracking of all variables and constraints
5. Systematic exploration of special cases

#### Input Format
```
---
**PROBLEM:**
[Complete problem statement]
---
```
Multiple problems follow the same structure if provided.'''