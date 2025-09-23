# Workflow ID: mbppplus_106_0
# Benchmark: mbppplus
# Data Indices: [201, 77]

import asyncio

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

        # Stage 1: Problem Decomposition and Classification
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into core components:
            1. Identify the primary task (e.g., transformation, search, calculation)
            2. Classify problem type: string, array, mathematical, logical, or mixed
            3. List all edge cases: empty inputs, single elements, duplicates, boundaries
            4. Note any constraints: time complexity, space complexity, immutability
            5. Extract exact function signature and return type requirements
            6. Determine if order preservation is required
            7. Identify if the solution can leverage built-in functions or requires custom logic
            Return structured subproblems with clear dependencies.""",
            context=""
        )

        # Stage 2: Parallel Solution Generation (3 perspectives)
        literal_solution, robust_solution, algorithmic_solution = await asyncio.gather(
            self.generate(
                instruction="""Generate a direct, literal solution that mirrors the examples exactly.
                - Focus on reproducing the demonstrated behavior
                - Use the simplest possible approach
                - Do not optimize prematurely
                - Include comments explaining each step
                - Handle only the cases shown in examples unless edge cases are obvious""",
                context=str(decomposition)
            ),
            self.generate(
                instruction="""Generate a robust, edge-case-aware solution.
                - Explicitly handle all edge cases identified in decomposition
                - Include input validation and defensive programming
                - Use clear, verbose variable names
                - Add comments for each edge case handled
                - Prioritize correctness over performance
                - Return appropriate defaults for empty/invalid inputs""",
                context=str(decomposition)
            ),
            self.generate(
                instruction="""Generate an algorithmic or mathematical reformulation.
                - Can this be solved with a known algorithm? (binary search, two pointers, etc.)
                - Is there a mathematical pattern or formula?
                - Can set operations, sorting, or other transformations simplify it?
                - Focus on efficiency and elegance
                - Include complexity analysis in comments
                - Only if applicable — don't force it if not natural""",
                context=str(decomposition)
            )
        )

        # Stage 3: Ensemble Synthesis
        synthesized_approach = await self.ensemble(
            instruction="""Synthesize the three solutions into one optimal implementation:
            1. Take the clarity and simplicity from the literal solution
            2. Incorporate the edge-case handling from the robust solution
            3. Adopt any algorithmic efficiency from the reformulation (if correct and applicable)
            4. Ensure the final approach matches the exact function signature
            5. Preserve order if required, handle empty inputs, return correct types
            6. Output should be a complete, self-contained implementation plan
            7. Include specific instructions for code generation: imports, type handling, edge cases""",
            contexts_list=[literal_solution, robust_solution, algorithmic_solution]
        )

        # Stage 4: Code Generation with Iterative Validation
        final_code = None
        for attempt in range(3):
            try:
                code_attempt = await self.programmer(
                    instruction=f"""Generate the final Python implementation:
                    {synthesized_approach}
                    
                    CRITICAL REQUIREMENTS:
                    - Use EXACT function name and parameters from problem
                    - Import any needed modules INSIDE the function if necessary
                    - Return correct data type (list, tuple, set, string, etc.)
                    - Handle empty inputs gracefully (return 0, empty string, etc. as appropriate)
                    - Preserve order if problem implies it
                    - No wrapper functions or classes
                    - Include brief comments for edge-case handling
                    - Code must be production-ready and pass all test cases including hidden ones""",
                    context=synthesized_approach,
                    max_retries=1
                )
                
                # Validate and refine
                validation = await self.revise(
                    instruction="""Critique this code against these criteria:
                    1. Does it handle empty input? 
                    2. Does it preserve order if required?
                    3. Does it return correct data type?
                    4. Are there off-by-one errors?
                    5. Does it match function signature exactly?
                    6. Are edge cases from decomposition handled?
                    If any issues, explain exactly what to fix. If perfect, say 'VALIDATED'.""",
                    context=code_attempt
                )
                
                if "VALIDATED" in validation.upper():
                    final_code = code_attempt
                    break
                else:
                    # Revise based on critique
                    synthesized_approach = await self.revise(
                        instruction=f"""Incorporate this critique into the implementation plan:
                        {validation}
                        
                        Update the approach to fix all identified issues while preserving strengths.
                        Be specific about what changes to make.""",
                        context=synthesized_approach
                    )
            except Exception as e:
                continue

        if final_code is None:
            # Fallback: return the synthesized approach as code
            final_code = await self.programmer(
                instruction=f"""Generate final implementation from this plan:
                {synthesized_approach}
                
                Follow all critical requirements from previous instructions.""",
                context=synthesized_approach
            )

        return final_code