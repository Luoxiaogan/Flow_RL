# Workflow ID: limr_106_0
# Benchmark: limr
# Data Indices: [305, 75]

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

        # PHASE 1: INITIAL DECOMPOSITION & CLASSIFICATION
        decomposition_plan = await self.generate(
            instruction="""Perform deep problem decomposition and classification:
            1. Identify the core mathematical domain(s): geometry, algebra, combinatorics, number theory, etc.
            2. Break the problem into atomic subproblems with clear inputs and outputs.
            3. For each subproblem, classify required techniques: proof, computation, transformation, etc.
            4. Flag any potential 'insight triggers' — non-obvious identities, theorems, or transformations.
            5. Estimate complexity level (low/medium/high) for each subproblem.
            6. Suggest multiple solution strategies per subproblem where applicable.
            Output as a structured JSON-like outline.""",
            context=""
        )

        # PHASE 2: PARALLEL SUBPROBLEM PROCESSING
        # Extract subproblems (simulated — in practice, parse decomposition_plan)
        subproblem_attempts = []
        strategies = [
            "algebraic manipulation and symbolic reasoning",
            "geometric interpretation and coordinate transformation",
            "combinatorial enumeration and case analysis",
            "number-theoretic properties and modular arithmetic"
        ]
        
        for strategy in strategies:
            attempt = await self.generate(
                instruction=f"""Solve the problem using {strategy}:
                - Start from first principles
                - Show all intermediate steps
                - Justify key assumptions
                - If stuck, note where and why
                - Format final answer as integer 000-999 if possible""",
                context=decomposition_plan
            )
            subproblem_attempts.append(attempt)

        # PHASE 3: ADVERSARIAL VALIDATION & REVISION
        validated_solutions = []
        for i, attempt in enumerate(subproblem_attempts):
            critique = await self.generate(
                instruction=f"""Critique this solution attempt #{i+1}:
                - Check for logical consistency and mathematical validity
                - Verify computational steps (if any)
                - Identify any violated constraints or assumptions
                - Flag domain mismatches (e.g., using real numbers when integers required)
                - Suggest specific revisions if errors found
                Be brutally honest — your goal is to break this solution.""",
                context=attempt
            )
            
            revised = await self.revise(
                instruction=f"""Revise the solution based on this critique:
                {critique}
                - Fix all identified errors
                - Strengthen weak justifications
                - Add missing steps
                - Preserve correct insights
                - Re-output as complete solution with final answer""",
                context=attempt
            )
            validated_solutions.append(revised)

        # PHASE 4: ENSEMBLE SYNTHESIS & FINAL VALIDATION
        synthesized = await self.ensemble(
            instruction="""Synthesize the best elements from all revised solutions:
            - Resolve contradictions by choosing mathematically sound approach
            - Combine complementary insights
            - Ensure final answer is consistent across valid approaches
            - Output single coherent solution with clear derivation
            - Final answer must be integer 000-999 format""",
            contexts_list=validated_solutions
        )

        # PHASE 5: COMPUTATIONAL VERIFICATION & FORMATTING
        final_answer = await self.programmer(
            instruction="""Extract the final numerical answer from the solution and verify computationally:
            - Parse the solution text to find the final integer answer
            - Re-compute independently using Python if possible
            - Validate against problem constraints
            - Format as 3-digit string with leading zeros (e.g., 42 → "042")
            - If multiple answers possible, choose the one consistent with all valid approaches""",
            context=synthesized,
            max_retries=3
        )

        # PHASE 6: SANITY CHECK & OUTPUT
        sanitized = await self.revise(
            instruction="""Final sanity check:
            - Is the answer an integer between 000 and 999?
            - Does it match the problem's expected format?
            - Are there any remaining logical inconsistencies?
            - If not, correct and output ONLY the 3-digit string.
            Output nothing else — just the 3-digit answer.""",
            context=final_answer
        )

        # Extract just the 3-digit answer using regex as fallback
        match = re.search(r'\b\d{3}\b', sanitized)
        if match:
            return match.group(0)
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d+', sanitized)
            for num in numbers:
                if len(num) <= 3:
                    return num.zfill(3)
            return "000"  # ultimate fallback