# Workflow ID: mgsmbn_94_0
# Benchmark: mgsmbn
# Data Indices: [49, 52]

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

        # STEP 1: CLASSIFY PROBLEM TYPE & EXTRACT ENTITIES
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and perform the following:
            1. Classify the problem type: Is it Sequential, Proportional, Rate-Based, Distribution, Multi-Entity, or Comparison?
            2. Extract all named entities: people, objects, institutions.
            3. Extract all numerical values and their contextual meaning (e.g., "5 players per team", "8 weeks").
            4. Identify units (টাকা, ঘণ্টা, জিনিস, etc.) and track their consistency.
            5. Note any implicit constraints (e.g., "can't have fractional people", "must be positive").
            6. Predict the expected answer format (integer, decimal, unit).
            Output in structured markdown format with clear headings.""",
            context=""
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION
        subproblems = await self.decompose(
            instruction="""Break down the problem into atomic, logically dependent subproblems.
            For each subproblem:
            - Assign a unique ID (e.g., SP1, SP2)
            - Write a clear, standalone description of what needs to be calculated or determined
            - List dependency IDs (comma-separated) — which subproblems must be solved first?
            - Flag if the subproblem involves unit conversion, reverse calculation, or constraint checking.
            Ensure the decomposition covers ALL steps needed to reach the final answer, including implicit ones.""",
            context=classification
        )

        # STEP 3: PARALLEL HYPOTHESIS GENERATION (4 STRATEGIES)
        hypothesis_tasks = [
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
                - Define variables for unknowns.
                - Write equations based on relationships in the problem.
                - Solve step by step, showing substitutions.
                - Verify solution against constraints.
                Context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using STEP-BY-STEP ARITHMETIC:
                - Perform calculations in chronological or logical order.
                - Show intermediate results explicitly.
                - Track units at every step.
                - Double-check additions, multiplications, divisions.
                Context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve with UNIT & CONSTRAINT AWARENESS:
                - Explicitly state units for every number.
                - Check unit consistency in operations.
                - Validate against real-world constraints (no negative people, etc.).
                - Adjust calculations if units mismatch.
                Context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve via BACKWARD REASONING (if applicable):
                - Start from the final state and reverse-engineer initial conditions.
                - Useful for problems like "ended with $100 after 8 weeks of $5/week".
                - Show reverse operations clearly.
                Context: {classification}""",
                context=""
            )
        ]
        
        hypotheses = await asyncio.gather(*hypothesis_tasks)

        # STEP 4: ENSEMBLE SYNTHESIS & VALIDATION
        ensemble_result = await self.ensemble(
            instruction="""Evaluate all candidate solutions and select the best one:
            - Check mathematical correctness of each step.
            - Verify unit consistency throughout.
            - Ensure answer respects real-world constraints (e.g., integer people).
            - Prefer solutions with clear, traceable reasoning.
            - If all solutions have flaws, synthesize a corrected version by combining their strongest parts.
            - Output the final answer as a single numerical value, and justify your selection.""",
            contexts_list=hypotheses
        )

        # STEP 5: PROGRAMMATIC VERIFICATION
        code_verification = await self.programmer(
            instruction=f"""Generate and execute Python code that replicates the exact calculations from the selected solution.
            Requirements:
            - Include all intermediate steps as variables.
            - Add assertions for unit consistency and boundary conditions (e.g., assert result >= 0).
            - Handle decimals with proper precision.
            - Output only the final numerical result.
            - If the code fails, revise and retry (max 3 attempts).
            Selected solution context: {ensemble_result}""",
            context=ensemble_result,
            max_retries=3
        )

        # STEP 6: EXTRACT NUMERICAL ANSWER (robust parsing)
        # Extract the first number (integer or decimal) from the final output
        match = re.search(r'(-?\d+\.?\d*)', code_verification)
        if match:
            final_answer = match.group(1)
            # Convert to int if it's a whole number
            if '.' in final_answer:
                final_answer = float(final_answer)
                if final_answer.is_integer():
                    final_answer = int(final_answer)
            else:
                final_answer = int(final_answer)
        else:
            # Fallback: extract from ensemble if code fails
            match = re.search(r'(-?\d+\.?\d*)', ensemble_result)
            if match:
                final_answer = match.group(1)
                if '.' in final_answer:
                    final_answer = float(final_answer)
                    if final_answer.is_integer():
                        final_answer = int(final_answer)
                else:
                    final_answer = int(final_answer)
            else:
                final_answer = 0  # Ultimate fallback (should rarely happen)

        return str(final_answer)