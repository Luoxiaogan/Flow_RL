# Workflow ID: mgsmbn_82_0
# Benchmark: mgsmbn
# Data Indices: [3]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: CLASSIFY PROBLEM TYPE & CONSTRAINTS
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem and classify it:

1. Problem Type: Choose primary category:
   - Sequential Operations (events in order)
   - Rate/Time/Distance (speed, work rate, unit price)
   - Proportional Reasoning (ratios, percentages, scaling)
   - Distribution (division, sharing, remainders)
   - Comparison (differences, "how many more")
   - Multi-entity (multiple actors with different quantities)

2. Constraints & Requirements:
   - Does it involve units? (টাকা, ঘণ্টা, কাপ, জন, etc.) List them.
   - Are there hidden steps or implicit calculations?
   - Must the answer be an integer? (e.g., people, chickens, whole items)
   - Is there a time sequence or chronological dependency?

3. Expected Solution Strategy:
   - What mathematical operations are likely needed? (add, sub, mul, div, mod, etc.)
   - Are intermediate variables or subproblems required?
   - What are the key entities and their relationships?

Output in this structured format:
TYPE: [type]
UNITS: [list of units or 'none']
INTEGER_CONSTRAINT: [yes/no]
HIDDEN_STEPS: [yes/no]
OPERATIONS: [list]
KEY_ENTITIES: [brief description]
""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Solve using MATHEMATICAL MODELING approach:
- Define variables for unknowns and knowns
- Translate Bengali relationships into algebraic equations
- Show step-by-step equation solving
- Maintain unit consistency throughout
- Final answer must be numerical only""",
            
            """Solve using CHRONOLOGICAL SIMULATION approach:
- Identify sequence of events as they occur in time
- Simulate each step with running totals or state changes
- Track quantities after each event
- Account for all mentioned actions in order
- Final answer must be numerical only""",
            
            """Solve using UNIT-FIRST REASONING approach:
- Explicitly track units for every number (e.g., '15 cups', '20 chickens')
- Reject any operation that combines incompatible units
- Perform unit conversions only when necessary, document them
- Ensure final answer has correct unit (then strip for output)
- Final answer must be numerical only"""
        ]

        # Add constraint-aware strategy if needed
        if "INTEGER_CONSTRAINT: yes" in classification:
            strategy_instructions.append("""Solve using INTEGER/CONSTRAINT-AWARE approach:
- Assume answer must be whole number (no fractions for people/items)
- Use floor/ceiling/modulo as appropriate
- Check for remainder handling in division
- Validate that answer makes sense in real-world context
- Final answer must be numerical only""")

        # Generate solutions in parallel
        strategy_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: CONDITIONAL DECOMPOSITION FOR COMPLEX PROBLEMS
        decomposition_needed = any(keyword in classification.lower() for keyword in ["multi-step", "hierarchical", "subproblem", "hidden_steps: yes"])
        
        if decomposition_needed:
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, independent subproblems:
- Each subproblem should be solvable with basic arithmetic
- Define clear inputs and outputs for each
- Specify dependencies between subproblems
- Focus on isolating calculations that can be verified independently
- Maximum 5 subproblems""",
                context=classification
            )
            
            # Solve subproblems (could be parallelized further but keeping simple for now)
            subproblem_solutions = []
            for subproblem in decomposition:
                sub_sol = await self.generate(
                    instruction=f"""Solve this subproblem:
{subproblem['description']}

Show calculation clearly. Output only the numerical result.""",
                    context=classification
                )
                subproblem_solutions.append(sub_sol)
            
            # Reconstruct final solution from subproblems
            reconstructed = await self.generate(
                instruction=f"""Combine these subproblem solutions into final answer:
Subproblems: {decomposition}
Solutions: {subproblem_solutions}

Show how they connect to form complete solution. Output only final numerical answer.""",
                context=classification
            )
            strategy_solutions.append(reconstructed)

        # STEP 4: ADVERSARIAL VALIDATION LOOP
        validated_solutions = []
        for i, solution in enumerate(strategy_solutions):
            current_solution = solution
            for revision_round in range(2):  # Up to 2 revision cycles
                validation = await self.revise(
                    instruction=f"""CRITICALLY EVALUATE THIS SOLUTION (Adversarial Mode):
Assume this solution is WRONG. Find the most likely error in:
- Arithmetic calculation
- Unit handling or conversion
- Missing hidden step
- Violation of integer constraint
- Misinterpretation of Bengali phrasing
- Chronological sequence error

If you find an error, explain it precisely. If no error, confirm why it's correct.
Output format: ERROR: [description] or VALID: [reason]""",
                    context=current_solution
                )
                
                if "ERROR:" in validation:
                    # Revise based on error
                    current_solution = await self.revise(
                        instruction=f"""FIX THE FOLLOWING ERROR:
{validation}

Revise the solution accordingly. Show corrected version with clear steps.
Output only the revised numerical answer and brief justification.""",
                        context=current_solution
                    )
                else:
                    break  # No errors found, solution validated
            
            validated_solutions.append(current_solution)

        # STEP 5: ENSEMBLE SYNTHESIS WITH CONFIDENCE SCORING
        final_answer = await self.ensemble(
            instruction="""Synthesize the best answer from these candidate solutions:

Evaluate each on:
1. Step-by-step clarity and logical flow
2. Unit consistency and proper handling
3. Alignment with problem constraints (integer, hidden steps, etc.)
4. Arithmetic correctness
5. Contextual plausibility (real-world sense)

Assign confidence 1-5 for each criterion. Select solution with highest total confidence.
If multiple high-confidence solutions agree, output their consensus.
If they disagree, synthesize by taking the most rigorously justified answer.

OUTPUT ONLY THE FINAL NUMERICAL VALUE. NO UNITS. NO EXPLANATIONS.""",
            contexts_list=validated_solutions
        )

        # STEP 6: PROGRAMMER VERIFICATION FOR NUMERICAL PRECISION (if needed)
        # Check if answer contains complex arithmetic that might need verification
        if any(op in classification for op in ["div", "fraction", "decimal", "large number"]):
            try:
                programmer_verification = await self.programmer(
                    instruction=f"""Convert this reasoning into executable Python code:
{final_answer}

Define all variables clearly. Show calculations step by step.
Output only the final numerical result as float or int.
Validate against original problem constraints.""",
                    context=classification,
                    max_retries=2
                )
                # Extract number from programmer output
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", programmer_verification)
                if numbers:
                    final_answer = numbers[0]  # Take first number found
            except Exception:
                # If programmer fails, stick with ensemble answer
                pass

        # STEP 7: FINAL SANITY CHECK & OUTPUT FORMATTING
        sanitized_answer = await self.generate(
            instruction=f"""FINAL SANITY CHECK:
Original problem: {self.problem_text}
Proposed answer: {final_answer}

Verify:
1. Is this a single numerical value? (integer or decimal)
2. Does it satisfy integer constraint if required?
3. Is it positive? (negative doesn't make sense for counts)
4. Does it match the scale of input numbers? (not absurdly large/small)

If any issue, correct it. Otherwise, output exactly the same number.
OUTPUT ONLY THE NUMBER. NOTHING ELSE.""",
            context=final_answer
        )

        # Extract just the number (in case any text slipped through)
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", sanitized_answer)
        if numbers:
            return numbers[0]
        else:
            # Fallback: return original if no number found (shouldn't happen)
            return final_answer