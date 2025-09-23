# Workflow ID: mbppplus_41_0
# Benchmark: mbppplus
# Data Indices: [287, 203, 225]

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

        # Step 1: Comprehensive problem decomposition
        decomposition = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Extract:
            1. Exact input types and constraints (e.g., tuples, lists, integers)
            2. Expected output type and format
            3. Key operations required (mathematical, logical, structural)
            4. Edge cases to consider (empty inputs, zeros, negatives, duplicates, single elements)
            5. Potential pitfalls or ambiguities in the problem statement
            6. Mathematical properties or invariants that could be leveraged
            Present this as a structured, detailed breakdown.""",
            context=""
        )

        # Step 2: Parallel solution generation - three strategic lanes
        direct_solution, edge_hardened_solution, math_verified_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct, clean Python implementation based on the problem description and examples.
                Use the exact function signature provided. Focus on clarity and simplicity.
                Problem decomposition context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a robust, edge-case-hardened Python implementation.
                Explicitly handle: empty inputs, single elements, type conversions, zero values, negative numbers, duplicates.
                Include defensive checks and clear error handling even if not explicitly required.
                Problem decomposition context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a mathematically or logically derived solution from first principles.
                Derive the solution using mathematical identities, logical proofs, or algorithmic invariants.
                Show your reasoning in comments if helpful, but return only the function code.
                Problem decomposition context: {decomposition}""",
                context=""
            )
        )

        # Step 3: Ensemble synthesis - combine the best of all worlds
        synthesized_solution = await self.ensemble(
            instruction="""You are an expert Python code reviewer and synthesizer. You have three candidate solutions:
            1. A direct implementation
            2. An edge-case hardened version
            3. A mathematically derived version
            
            Your task: Synthesize a single optimal solution by:
            - Taking the clearest structure from the direct implementation
            - Incorporating robust edge-case handling from the hardened version
            - Validating and correcting logic using mathematical principles from the third version
            - Preserving the exact function signature and return type
            - Ensuring efficiency and Pythonic style
            Return ONLY the final function code, no explanations.""",
            contexts_list=[direct_solution, edge_hardened_solution, math_verified_solution]
        )

        # Step 4: Critical revision and bug fixing
        revised_solution = await self.revise(
            instruction="""Critically analyze this code for:
            - Logical errors or flawed conditions
            - Type mismatches (e.g., returning list instead of tuple)
            - Inefficiencies or unnecessary complexity
            - Deviations from problem requirements
            - Failure to handle edge cases mentioned in decomposition
            Fix any issues found. Pay special attention to the test cases shown in the original problem.
            Return the corrected, production-ready code.""",
            context=synthesized_solution
        )

        # Step 5: Final sanity check and summarization
        final_summary = await self.summarize(
            instruction="""Extract and verify:
            1. Function signature matches exactly
            2. Return type is correct
            3. Core logic aligns with problem requirements
            4. Edge cases from decomposition are handled
            If any mismatch, flag it. Otherwise, confirm readiness.""",
            context=revised_solution
        )

        # Fallback: if summary indicates problems, return original synthesized (better than broken revised)
        if any(keyword in final_summary.lower() for keyword in ['mismatch', 'error', 'fail', 'incorrect']):
            return synthesized_solution
        
        return revised_solution