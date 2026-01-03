# Workflow ID: mgsmbn_22_0
# Benchmark: mgsmbn
# Data Indices: [41, 142]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: SEMANTIC DECOMPOSITION — Extract entities, quantities, relationships, and target
        decomposition = await self.generate(
            instruction="""Perform a deep semantic decomposition of this Bengali math problem. Identify:
            1. All named entities (people, objects, days, etc.) and their roles.
            2. All numerical values and what they represent (units, counts, rates, etc.).
            3. Temporal or logical sequence of events (if any).
            4. Mathematical relationships (additive, multiplicative, proportional, comparative).
            5. The explicit or implicit target variable (what we're solving for).
            6. Any constraints or real-world limitations (e.g., no negative items, whole people).
            
            Format your output as a structured markdown list with clear section headers. Be exhaustive and precise.
            Example:
            ## Entities:
            - Mechanic: earns different rates for truck vs car tires
            - Thursday: repaired 6 truck tires, 4 car tires
            - Friday: repaired 12 car tires, 0 truck tires
            
            ## Quantities:
            - Truck tire rate: $60
            - Car tire rate: $40
            - Thursday earnings: (6 * 60) + (4 * 40)
            - Friday earnings: (12 * 40) + (0 * 60)
            
            ## Target:
            - Difference in earnings between higher-earning day and lower-earning day""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION STRATEGIES — Generate 3 distinct approaches
        solution_strategies = [
            "Solve chronologically: compute each day/event step by step, then combine results.",
            "Solve algebraically: set up equations with variables, then solve symbolically.",
            "Solve by unit analysis: track earnings per unit type, then aggregate by day/event."
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using this decomposition:
                {decomposition}

                Now solve the problem using the following strategy:
                {strategy}

                Show ALL intermediate steps. Label each calculation. Track units explicitly.
                Finally, box your final numerical answer as: \\boxed{{<number>}}""",
                context=decomposition
            ) for strategy in solution_strategies]
        )

        # STEP 3: VALIDATION — Check each solution for common errors
        async def validate_solution(solution_text):
            return await self.generate(
                instruction=f"""Critically validate this solution:
                {solution_text}

                Check for:
                - Arithmetic errors (recompute key steps)
                - Unit mismatches or missing units
                - Violation of real-world constraints (e.g., negative people, fractional items unless allowed)
                - Misinterpretation of target (e.g., computed total instead of difference)
                - Logical sequence errors (e.g., applied operations in wrong order)

                If no errors, respond with "VALID".
                If errors found, describe them concisely and suggest correction.""",
                context=solution_text
            )

        validations = await asyncio.gather(
            *[validate_solution(sol) for sol in solution_attempts]
        )

        # STEP 4: CONDITIONAL REVISION — Only revise solutions that failed validation
        revised_solutions = []
        for i, (sol, val) in enumerate(zip(solution_attempts, validations)):
            if "VALID" not in val.upper():
                revised = await self.revise(
                    instruction=f"""This solution has validation issues:
                    {val}

                    Revise the solution to fix these errors. Maintain the original strategy.
                    Show corrected steps clearly. Preserve unit tracking and intermediate labels.
                    End with boxed final answer: \\boxed{{<number>}}""",
                    context=sol
                )
                revised_solutions.append(revised)
            else:
                revised_solutions.append(sol)

        # STEP 5: ENSEMBLE SYNTHESIS — Select or merge the best solution
        final_answer = await self.ensemble(
            instruction="""You are given multiple solution attempts for a Bengali math word problem.
            Select the most accurate, clearly reasoned, and error-free solution.
            If multiple are valid, choose the one with the clearest step-by-step justification.
            If they differ, synthesize a hybrid that combines the strongest elements.

            IMPORTANT: Extract ONLY the final numerical answer from the chosen solution.
            Return ONLY the number (integer or decimal), nothing else. No units. No explanation.
            Example: 40 or 15.5""",
            contexts_list=revised_solutions
        )

        # STEP 6: FINAL EXTRACTION — Ensure output is clean numerical value
        # Use regex to extract number from ensemble output (defensive programming)
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer.strip())
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return final_answer.strip()