# Workflow ID: mgsmbn_23_0
# Benchmark: mgsmbn
# Data Indices: [112]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for solving MGSM Bengali math word problems.
        Uses parallel generation, iterative validation, and ensemble synthesis.
        """
        import asyncio
        import re

        # Step 1: Comprehensive problem decomposition
        decomposition = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem. Extract and structure:

1. ALL numerical values with their units and what they represent (e.g., "7.50 টাকা per sandwich")
2. The unknown being asked for (clearly state what we need to find)
3. Temporal or logical sequence of events (what happens first, second, etc.)
4. Mathematical relationships (percentages, ratios, totals, differences)
5. Real-world constraints (can't have negative items, must be whole numbers, etc.)
6. Potential pitfalls or tricky elements (e.g., fees applied after subtotal, tips added last)

Format as a structured markdown list with clear headings. Be exhaustive.""",
            context=""
        )

        # Step 2: Generate multiple solution approaches in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Using this decomposition:
{decomposition}

Solve the problem using a STEP-BY-STEP CHRONOLOGICAL approach:
- Follow the exact sequence of events as described
- Show intermediate calculations with units
- Apply operations in correct order (e.g., percentage before addition)
- Track units at every step
- Box the final answer

Write out reasoning like a teacher explaining to a student.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Using this decomposition:
{decomposition}

Solve the problem using an ALGEBRAIC MODELING approach:
- Define variables for unknowns
- Write equations representing relationships
- Solve systematically
- Show all work with units
- Verify solution makes sense in context
- Box the final answer

Focus on mathematical rigor and symbolic representation.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Using this decomposition:
{decomposition}

Solve the problem using UNIT TRACKING and DIMENSIONAL ANALYSIS:
- Start with what you need to find (target unit)
- Work backwards or forwards using unit conversions
- Ensure every operation maintains dimensional consistency
- Show unit cancellation explicitly
- Box the final answer

Emphasize unit awareness and dimensional correctness.""",
                context=decomposition
            )
        )

        # Step 3: Validate each solution attempt
        validations = await asyncio.gather(
            *[self.revise(
                instruction="""Critically validate this solution:
1. Check arithmetic accuracy (recalculate key steps)
2. Verify order of operations (especially percentages, taxes, fees)
3. Confirm unit consistency throughout
4. Ensure answer matches what was asked for
5. Assess real-world plausibility (e.g., no negative money, reasonable magnitudes)
6. Identify any logical gaps or assumptions

If errors found, explain exactly what's wrong and how to fix it.
If correct, confirm with "VALID: [reason]".

Be brutally honest and precise.""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # Step 4: Synthesize best solution via ensemble
        best_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution from these options:

Evaluation criteria (in order of priority):
1. Mathematical correctness (arithmetic, order of operations)
2. Unit consistency and tracking
3. Step-by-step clarity and justification
4. Alignment with problem's chronological/logical sequence
5. Real-world plausibility

If one solution is clearly superior, select it.
If multiple are valid, synthesize a hybrid that combines their strengths.
If all have flaws, create a corrected version addressing all identified issues.

Output ONLY the final solution with clear steps and boxed answer.""",
            contexts_list=[f"Solution Attempt:\n{sol}\n\nValidation:\n{val}" 
                          for sol, val in zip(solution_attempts, validations)]
        )

        # Step 5: Iterative refinement (up to 2 rounds)
        current_solution = best_solution
        for iteration in range(2):
            refinement_check = await self.generate(
                instruction=f"""Review this solution for any remaining issues:
{current_solution}

Specifically check:
- Is the final answer a single numerical value?
- Are all intermediate steps correct?
- Is the unit handling perfect?
- Does it fully answer the original question?

If perfect, respond with "PERFECT".
If minor improvements needed, provide specific revision instructions.
If major errors, explain what's wrong and how to fix.""",
                context=current_solution
            )
            
            if "PERFECT" in refinement_check.upper():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Improve this solution based on feedback:
{refinement_check}

Requirements:
- Fix all identified issues
- Maintain step-by-step clarity
- Preserve unit tracking
- Ensure final answer is boxed and numerical
- Do not change correct parts unnecessarily""",
                    context=current_solution
                )

        # Step 6: Extract clean numerical answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from this solution.
- Remove all text, units, and explanations
- If answer is in a box (like \\boxed{29}), extract just the number
- If decimal, preserve exact precision
- If fraction, convert to decimal unless specified otherwise
- Output should be a single number string (e.g., "29", "15.5")

Example: If solution says "Therefore, the total is \\boxed{29} টাকা", output "29".""",
            context=current_solution
        )

        # Clean up answer (remove any remaining non-numeric characters)
        cleaned_answer = re.sub(r'[^\d\.]', '', final_answer.strip())
        
        return cleaned_answer