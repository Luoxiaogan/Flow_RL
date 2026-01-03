# Workflow ID: limr_9_0
# Benchmark: limr
# Data Indices: [113, 209]

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
        import json

        # STEP 1: Decompose the problem into subproblems with dependencies
        decomposition_instruction = """
        Systematically decompose the given mathematical problem into atomic subproblems.
        For each subproblem:
        - Clearly state what needs to be solved or proven
        - Identify the mathematical domain (algebra, geometry, number theory, combinatorics, etc.)
        - List any prerequisite knowledge or prior subproblems it depends on
        - Estimate whether it is primarily analytical, computational, or proof-based
        Output in structured format with id, description, and dependencies.
        """
        subproblems = await self.decompose(instruction=decomposition_instruction, context="")

        # STEP 2: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """
            Approach this problem from an ALGEBRAIC perspective. 
            - Look for symmetries, substitutions, or functional equations.
            - Express unknowns in terms of knowns.
            - Derive step-by-step symbolic manipulations.
            - If recursion is involved, attempt to find closed-form or invariant.
            """,
            """
            Approach this problem from a GEOMETRIC/COORDINATE perspective.
            - Assign coordinates or vectors if applicable.
            - Use transformations, reflections, or distance formulas.
            - Leverage properties of shapes, angles, or loci.
            - Translate geometric constraints into algebraic equations.
            """,
            """
            Approach this problem from a NUMBER THEORETIC or COMBINATORIAL perspective.
            - Factorize, use modular arithmetic, or consider divisibility.
            - Count cases systematically or use generating functions.
            - Look for patterns, invariants, or extremal principles.
            - Consider small cases or mathematical induction.
            """,
            """
            Approach this problem from a CALCULUS or OPTIMIZATION perspective.
            - Define functions to maximize/minimize.
            - Take derivatives, find critical points.
            - Use inequalities (AM-GM, Cauchy-Schwarz, etc.) if applicable.
            - Consider boundary behavior or asymptotic analysis.
            """
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # STEP 3: Attempt computational verification in parallel for promising candidates
        programmer_instruction = """
        Convert the following mathematical reasoning into executable Python code.
        - Implement all necessary calculations precisely.
        - Handle edge cases and validate inputs.
        - The final output must be an integer between 000 and 999.
        - If multiple answers are possible, return the one specified by the problem constraints.
        - Do not use symbolic libraries unless absolutely necessary; prefer numerical computation.
        - Print only the final integer answer.
        """

        # Select top 2 strategies for computational verification (could be extended to all)
        programmer_tasks = [
            self.programmer(instruction=programmer_instruction, context=attempt, max_retries=3)
            for attempt in strategy_attempts[:2]
        ]
        computational_results = await asyncio.gather(*programmer_tasks, return_exceptions=True)

        # Filter out failed computations
        valid_computational_results = [
            str(res) for res in computational_results 
            if isinstance(res, str) and res.strip().isdigit() and 0 <= int(res.strip()) <= 999
        ]

        # STEP 4: Revise analytical solutions iteratively for rigor
        revised_analytical_attempts = []
        for attempt in strategy_attempts:
            current = attempt
            for iteration in range(2):  # Two rounds of revision
                revision_instruction = f"""
                Critically revise the following mathematical solution:
                - Check for logical gaps, unjustified assumptions, or algebraic errors.
                - Verify that all steps follow from previous ones.
                - Ensure the final answer is an integer between 000 and 999.
                - If recursion or induction is used, confirm the base case and inductive step.
                - Improve clarity and add missing derivations.
                - Preserve the original approach but correct and deepen the reasoning.
                """
                current = await self.revise(instruction=revision_instruction, context=current)
            revised_analytical_attempts.append(current)

        # STEP 5: Ensemble synthesis — combine computational and revised analytical results
        all_candidates = valid_computational_results + revised_analytical_attempts

        if len(all_candidates) == 0:
            # Fallback: generate a default comprehensive solution
            fallback_instruction = """
            Solve the problem comprehensively using the most straightforward mathematical approach.
            Show all steps clearly. Derive the answer rigorously. Ensure the result is an integer between 000 and 999.
            """
            fallback_solution = await self.generate(instruction=fallback_instruction, context="")
            all_candidates = [fallback_solution]

        ensemble_instruction = """
        You are given multiple solution attempts for a mathematical problem.
        Some are computational outputs (integers), others are analytical derivations.
        Your task:
        1. Evaluate each for mathematical correctness, completeness, and adherence to problem constraints.
        2. If computational results agree with analytical derivations, return that integer.
        3. If there is disagreement, select the solution with the most rigorous and complete derivation.
        4. If all else fails, choose the most plausible answer based on logical consistency.
        5. OUTPUT ONLY THE FINAL INTEGER ANSWER BETWEEN 000 AND 999. NO EXPLANATIONS.
        """

        final_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=all_candidates
        )

        # Ensure output is clean integer string
        try:
            answer_int = int(final_answer.strip())
            if 0 <= answer_int <= 999:
                return f"{answer_int:03d}"  # Zero-pad to 3 digits
            else:
                return "000"  # Fallback
        except:
            return "000"  # Ultimate fallback