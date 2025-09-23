# Workflow ID: mbppplus_88_0
# Benchmark: mbppplus
# Data Indices: [94, 86, 176]

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
        Universal workflow for programming problem-solving domain.
        Dynamically adapts strategy based on problem semantics.
        """
        import asyncio
        import re

        # STEP 1: Deep problem decomposition and constraint extraction
        decomposition = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem:
            1. Extract exact function signature and parameter types
            2. Identify expected return type and format
            3. List all explicit constraints from description and test cases
            4. Infer implicit constraints (edge cases: empty inputs, single elements, negatives, duplicates)
            5. Classify problem type (e.g., mathematical, data structure, comparison, transformation)
            6. Hypothesize core algorithmic pattern needed
            7. Flag any ambiguities in requirements
            Output as structured analysis with clear sections.""",
            context=""
        )

        # STEP 2: Parallel solution generation with diverse strategies
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution using EMPIRICAL strategy:
                - Base logic strictly on provided test cases
                - Prioritize replicating exact outputs
                - Minimal generalization beyond examples
                - Include handling for obvious edge cases
                - Return ONLY the function implementation with necessary imports inside
                Problem context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution using THEORETICAL strategy:
                - Apply known algorithmic patterns (e.g., recursion, iteration, set operations)
                - Prioritize mathematical/logical correctness
                - Generalize beyond test cases
                - Include comprehensive edge case handling
                - Return ONLY the function implementation with necessary imports inside
                Problem context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution using DEFENSIVE strategy:
                - Assume worst-case inputs (empty, invalid types, extremes)
                - Add explicit type/length checks if needed
                - Prioritize robustness over elegance
                - Document assumptions as comments
                - Return ONLY the function implementation with necessary imports inside
                Problem context: {decomposition}""",
                context=""
            )
        )

        # STEP 3: Parallel revision for correctness and edge case coverage
        revised_solutions = await asyncio.gather(*[
            self.revise(
                instruction=f"""Critically revise this solution:
                - Verify it handles ALL edge cases from decomposition: {decomposition}
                - Check data type consistency (list vs tuple vs set)
                - Validate against provided test cases
                - Fix off-by-one errors, boundary conditions
                - Ensure no silent assumptions (e.g., sorted input, positive numbers)
                - Optimize only if correctness is guaranteed
                - Return ONLY clean function implementation""",
                context=sol
            ) for sol in solution_attempts
        ])

        # STEP 4: Ensemble synthesis with ambiguity resolution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from all candidates:
            1. Compare all revised solutions
            2. Identify strongest logic for core functionality
            3. Incorporate best edge-case handling from each
            4. Resolve conflicts by prioritizing: correctness > edge-case coverage > efficiency
            5. If fundamental disagreements exist (e.g., order preservation), flag and resolve using problem decomposition
            6. Return ONLY the final function implementation with exact signature and necessary imports inside""",
            contexts_list=revised_solutions
        )

        # STEP 5: Format enforcement and cleanup
        cleaned_solution = await self.revise(
            instruction="""Final cleanup:
            - Extract ONLY the function implementation (no markdown, no explanations)
            - Ensure function signature exactly matches original
            - Move all imports inside the function if present
            - Remove any debug prints or extra comments
            - Validate return type matches expected output
            - Return pure, production-ready code""",
            context=final_solution
        )

        # Extract code block if present
        code_match = re.search(r'