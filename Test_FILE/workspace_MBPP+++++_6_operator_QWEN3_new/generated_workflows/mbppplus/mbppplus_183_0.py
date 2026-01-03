# Workflow ID: mbppplus_183_0
# Benchmark: mbppplus
# Data Indices: [198, 338]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving.
        Uses parallel analysis, synthesis, and adaptive code generation.
        """
        import asyncio

        # Phase 1: Parallel multi-perspective analysis
        # Generate three independent analytical perspectives simultaneously
        perspective_tasks = [
            self.generate(
                instruction="""Analyze the PROBLEM TASK from a LITERAL perspective:
                - What is the explicit, surface-level operation being requested?
                - What are the input parameters and expected output?
                - Extract any explicit examples or test cases.
                - State the task in the simplest possible terms.
                Format as a clear, concise paragraph.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the PROBLEM TASK from a CONSTRAINTS & ASSUMPTIONS perspective:
                - What are the implicit constraints or assumptions?
                - What data types are involved? Are there type conversion needs?
                - Are there hidden requirements (e.g., performance, memory)?
                - What edge cases might exist (empty inputs, boundary values)?
                - Are there domain-specific conventions (e.g., bit-width for bitwise ops)?
                Format as a structured list with clear headings.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the PROBLEM TASK from an EDGE CASES & ROBUSTNESS perspective:
                - What are ALL possible edge cases? (empty, single element, max/min values, duplicates)
                - How should errors or invalid inputs be handled?
                - What are the failure modes? Where might implementations commonly fail?
                - Are there special values (None, 0, negative numbers, empty strings) to consider?
                - Should the solution be defensive? Validate inputs?
                Format as a comprehensive checklist.""",
                context=""
            )
        ]
        
        # Execute all perspectives in parallel
        perspectives = await asyncio.gather(*perspective_tasks)
        
        # Phase 2: Synthesize perspectives into a unified solution blueprint
        solution_blueprint = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a SINGLE, COMPREHENSIVE SOLUTION BLUEPRINT:
            - Combine the literal task description with constraints and edge cases.
            - Create a step-by-step implementation strategy.
            - Specify exact data types and handling requirements.
            - Include explicit instructions for edge case handling.
            - Define the expected function signature and return type.
            - Provide pseudo-code or algorithmic steps if helpful.
            The blueprint should be detailed enough for direct code implementation.
            Format as a well-structured document with clear sections.""",
            contexts_list=perspectives
        )
        
        # Phase 3: Generate code from blueprint with retries
        # First attempt
        code_result = await self.programmer(
            instruction=f"""Implement the solution based on this BLUEPRINT:
            {solution_blueprint}
            
            CRITICAL REQUIREMENTS:
            - Output ONLY the Python function implementation (no explanations, no markdown).
            - Use the EXACT function name and parameters from the problem.
            - Include necessary imports INSIDE the function if needed.
            - Handle ALL edge cases identified in the blueprint.
            - Return appropriate data types as specified.
            - Ensure the code is production-ready and passes rigorous testing.
            - If the problem involves bit operations, assume 32-bit integers unless specified otherwise.
            - For sorting, preserve stability unless order is explicitly specified.
            
            EXAMPLE OUTPUT FORMAT: