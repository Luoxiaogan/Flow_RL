# Workflow ID: mgsmbn_30_0
# Benchmark: mgsmbn
# Data Indices: [20]

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
        import math

        # STEP 1: CLASSIFY & SEMANTIC NORMALIZATION
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify its type. Identify:
            - Primary mathematical domain (arithmetic, rate, proportion, distribution, comparison, multi-entity)
            - Key entities (people, objects, units like টাকা, ঘণ্টা, জিনিস)
            - Explicit and implicit numerical relationships
            - Required operations (addition, multiplication, division, percentage, etc.)
            - Constraints (non-negative, integer-only, unit consistency)
            - Temporal or sequential dependencies
            Output a structured classification with clear labels for each category.""",
            context=""
        )

        # STEP 2: SEMANTIC NORMALIZATION - CONVERT NARRATIVE TO STRUCTURED QUANTITIES
        normalized = await self.generate(
            instruction=f"""Given this classification:
            {classification}

            Rewrite the problem in a standardized mathematical Bengali format:
            - Extract all numerical values and assign them to variables with units
            - Convert narrative relationships into mathematical expressions
            - Eliminate honorifics, colloquialisms, and redundant phrasing
            - Preserve all constraints and conditions
            Output ONLY the normalized version, no explanations.""",
            context=classification
        )

        # STEP 3: CONDITIONAL DECOMPOSITION BASED ON CLASSIFICATION
        if "rate" in classification.lower() or "প্রতি" in self.problem_text or "per" in self.problem_text.lower():
            decomposition_strategy = """Decompose as a rate problem:
            1. Identify base rate (quantity per unit time/item)
            2. Identify total duration/quantity
            3. Calculate total consumption
            4. Map to cost/availability units
            5. Apply unit conversions
            Dependencies: Each step depends on the previous."""
        elif "distribution" in classification.lower() or "ভাগ" in self.problem_text:
            decomposition_strategy = """Decompose as a distribution problem:
            1. Identify total quantity to distribute
            2. Identify number of recipients or groups
            3. Calculate per-unit share
            4. Handle remainders or constraints
            5. Verify integer constraints if applicable
            Dependencies: Steps 1-2 before 3, 3 before 4-5."""
        else:
            decomposition_strategy = """Decompose as a general arithmetic problem:
            1. Identify all given numerical values and their meanings
            2. Identify the unknown to solve for
            3. Determine sequence of operations
            4. Identify intermediate calculations needed
            5. Verify unit consistency at each step
            Dependencies: Logical sequence based on mathematical dependencies."""

        subproblems = await self.decompose(
            instruction=f"""{decomposition_strategy}
            Use the normalized problem text as reference. Each subproblem must be self-contained with clear inputs and expected outputs. Include unit tracking in each description.""",
            context=normalized
        )

        # STEP 4: PARALLEL SUBPROBLEM SOLVING WITH MULTIPLE STRATEGIES
        async def solve_subproblem(subproblem_desc, subproblem_id):
            # Strategy 1: Direct mathematical formulation
            strategy1 = await self.generate(
                instruction=f"""Subproblem {subproblem_id}: {subproblem_desc}
                Formulate a precise mathematical expression or equation to solve this subproblem. Show variable definitions and unit tracking. Do not compute yet.""",
                context=normalized
            )
            
            # Strategy 2: Step-by-step procedural reasoning
            strategy2 = await self.generate(
                instruction=f"""Subproblem {subproblem_id}: {subproblem_desc}
                Solve through step-by-step procedural reasoning. Write out each calculation explicitly with intermediate results. Track units at every step.""",
                context=normalized
            )
            
            # Ensemble the two strategies
            solution = await self.ensemble(
                instruction=f"""Subproblem {subproblem_id}: {subproblem_desc}
                Compare and synthesize the two solution strategies below. Select the most accurate and complete solution. Ensure unit consistency and constraint adherence.
                If they conflict, identify the error and produce a corrected version.
                Output ONLY the final solution for this subproblem, with units.""",
                contexts_list=[strategy1, strategy2]
            )
            return solution

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp['description'], sp['id']) for sp in subproblems]
        )

        # Create solution mapping for dependency resolution
        solution_map = {sp['id']: sol for sp, sol in zip(subproblems, subproblem_solutions)}

        # STEP 5: VALIDATE AND INTEGRATE SOLUTIONS
        integrated_solution = await self.generate(
            instruction=f"""Integrate all subproblem solutions into a complete answer:
            Subproblem Solutions: {solution_map}
            
            Steps:
            1. Verify that all dependencies are satisfied (solutions used in correct order)
            2. Check unit consistency across all steps
            3. Validate against real-world constraints (no negative quantities, fractional people, etc.)
            4. Combine results to produce the final numerical answer
            5. Double-check arithmetic for any calculation errors
            
            Output the final answer as a single numerical value with units if applicable, but the final output for the system should be just the number.""",
            context="\n".join(subproblem_solutions)
        )

        # STEP 6: PROGRAMMATIC VERIFICATION
        code_verification = await self.programmer(
            instruction=f"""Generate Python code to verify the final answer:
            Problem: {self.problem_text}
            Normalized: {normalized}
            Classification: {classification}
            Final Answer: {integrated_solution}
            
            Write code that:
            - Defines all variables from the problem
            - Implements the mathematical relationships
            - Computes the result
            - Validates against constraints (assert statements for non-negative, integer if required)
            - Prints only the final numerical result
            
            If the code produces a different result, flag the discrepancy.""",
            context=integrated_solution
        )

        # STEP 7: FINAL REVISION AND VALIDATION
        final_answer = await self.revise(
            instruction=f"""Review the entire solution process:
            - Does the final answer match the code verification result?
            - Are all units handled correctly?
            - Does the answer satisfy real-world constraints?
            - Is the numerical format correct (integer or decimal as appropriate)?
            
            If any issues are found, correct them and output only the final numerical answer.
            If no issues, output the answer as is.
            
            Code Verification: {code_verification}
            Integrated Solution: {integrated_solution}""",
            context=integrated_solution
        )

        # STEP 8: EXTRACT PURE NUMERICAL ANSWER
        pure_number = await self.generate(
            instruction="""Extract ONLY the numerical value from the text below. Remove all units, explanations, and formatting. If the number is decimal, preserve the exact decimal places. Output nothing else.""",
            context=final_answer
        )

        return pure_number.strip()