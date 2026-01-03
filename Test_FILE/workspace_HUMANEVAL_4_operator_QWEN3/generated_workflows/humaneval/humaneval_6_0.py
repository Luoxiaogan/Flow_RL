# Workflow ID: humaneval_6_0
# Benchmark: humaneval
# Data Indices: [47, 155]

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
        Universal code generation workflow for example-driven specification problems.
        Dynamically adapts to problem type, infers edge cases, validates symbolically,
        and synthesizes robust implementations.
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL ANALYSIS FORK
        # Extract three critical dimensions simultaneously
        example_analysis, problem_classification, edge_case_inventory = await asyncio.gather(
            self.generate(
                instruction="""Analyze the provided examples in the docstring with extreme precision.
                For each example:
                - Parse input and expected output
                - Note exact data types (int, float, tuple, etc.)
                - Identify patterns in transformation (e.g., sorting, digit counting, mathematical operations)
                - Detect any type coercion rules (e.g., int vs float returns)
                - List all observed edge cases (empty inputs, single elements, negatives, zeros)
                Format as structured markdown with clear sections.""",
                context=""
            ),
            self.generate(
                instruction="""Classify this problem by type and required operations:
                1. Primary domain: numerical, string, list, logical, or algorithmic?
                2. Core operations needed: sorting, iteration, recursion, mathematical formula, etc.
                3. Expected output structure: scalar, tuple, list, or other?
                4. Special considerations: mutability, side effects, performance constraints?
                5. Common algorithmic patterns this resembles (e.g., median, digit counting, sliding window)
                Provide detailed classification with justification from examples.""",
                context=""
            ),
            self.generate(
                instruction="""Generate a comprehensive edge case inventory for this problem type:
                - List 5-10 common edge cases not necessarily shown in examples
                - For each, explain why it's relevant and how it might break naive solutions
                - Prioritize by likelihood and severity
                - Include: empty inputs, single elements, extreme values, type boundaries, etc.
                Structure as numbered list with brief explanations.""",
                context=""
            )
        )

        # PHASE 2: ALGORITHM HYPOTHESIS GENERATION
        # Generate multiple candidate solutions based on analysis
        candidate_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Algorithm Candidate A:
                Based on the following analysis:
                {example_analysis}
                
                And problem classification:
                {problem_classification}
                
                Implement a straightforward, literal interpretation of the examples.
                Focus on correctness over elegance. Include detailed comments explaining each step.
                Ensure function signature matches ENTRY POINT exactly.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Algorithm Candidate B:
                Based on the same analysis but take a more mathematical/optimized approach.
                Look for formulas, patterns, or built-in functions that could simplify the solution.
                Still ensure exact match with examples and correct return types.
                Include comments justifying your mathematical choices.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Algorithm Candidate C:
                Based on edge case inventory:
                {edge_case_inventory}
                
                Design a defensive, robust solution that explicitly handles all listed edge cases.
                Even if not shown in examples, include guards for empty inputs, type checks, etc.
                Prioritize correctness and completeness over performance.
                Comment each edge case handling section.""",
                context=""
            )
        )

        # PHASE 3: SYMBOLIC VALIDATION & REFINEMENT
        # Validate each candidate against examples and edge cases
        validated_candidates = []
        for i, candidate in enumerate(candidate_solutions):
            validated = await self.revise(
                instruction=f"""CRITICAL VALIDATION STEP:
                You are a senior code reviewer. Validate this candidate solution against:
                1. Original examples from specification
                2. Inferred edge cases from analysis
                3. Return type requirements (int vs float, tuple structure, etc.)
                4. Function signature exact match
                
                For each example and edge case:
                - Mentally execute the code step by step
                - Verify output matches expected result exactly
                - Check for type consistency
                - Identify any flaws or missing cases
                
                If flaws found, revise the code to fix them.
                If no flaws, return the code unchanged.
                Preserve all comments and structure.
                Return ONLY the corrected Python code, nothing else.""",
                context=candidate
            )
            validated_candidates.append(validated)

        # PHASE 4: ENSEMBLE SYNTHESIS
        # Combine the best aspects of all validated candidates
        final_solution = await self.ensemble(
            instruction="""SYNTHESIS INSTRUCTION:
            You are given 3 validated candidate solutions. Your task:
            1. Compare all solutions for correctness, completeness, and elegance
            2. Identify the strongest aspects of each (e.g., Candidate A's clarity, Candidate B's efficiency, Candidate C's robustness)
            3. Synthesize a final solution that:
               - Passes all original examples
               - Handles all critical edge cases
               - Uses the most appropriate algorithmic approach
               - Has clean, minimal code
               - Matches function signature exactly
               - Returns correct types in all cases
            4. Remove any unnecessary comments or defensive code that doesn't add value
            5. Return ONLY the final Python function code, nothing else.
            
            CRITICAL: The output must be executable Python code with exact function signature from ENTRY POINT.""",
            contexts_list=validated_candidates
        )

        # PHASE 5: FINAL SANITY CHECK & CLEANUP
        # Ensure output is clean, executable code
        cleaned_solution = await self.revise(
            instruction="""FINAL SANITY CHECK:
            You are the last line of defense before code submission.
            Verify that this code:
            1. Is valid Python syntax
            2. Has exactly the function signature specified in ENTRY POINT
            3. Contains no markdown, explanations, or extra text
            4. Returns correct types as demonstrated in examples
            5. Is minimal and focused (no over-engineering)
            
            If any issues found, fix them immediately.
            Return ONLY the clean Python code, nothing else.""",
            context=final_solution
        )

        return cleaned_solution