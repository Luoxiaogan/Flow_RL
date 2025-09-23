# Workflow ID: mbppplus_12_0
# Benchmark: mbppplus
# Data Indices: [229, 227]

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

        # PHASE 1: Specification Extraction and Problem Decomposition
        specification = await self.generate(
            instruction="""Analyze the programming problem with extreme precision. Extract:
            1. Exact function signature required (name, parameters, return type)
            2. Core task in one sentence
            3. Input constraints and edge cases (empty, null, extreme values)
            4. Output format requirements (data type, structure, precision)
            5. Any implicit assumptions from test cases
            Format as a structured markdown list with clear headers.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Break this programming problem into minimal, testable subproblems. For each:
            - What atomic operation must be performed?
            - What edge cases must be handled?
            - What validation criteria must be met?
            Prioritize subproblems that address potential failure points.""",
            context=specification
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_instructions = [
            """Generate a direct, efficient implementation using built-in functions and standard library.
            Focus on readability and leveraging Python's strengths. Include all necessary imports.
            Handle edge cases explicitly. Match exact return type from specification.""",
            
            """Generate an implementation using explicit loops and manual logic (no built-in helpers).
            Focus on educational clarity and step-by-step processing. Include detailed comments.
            Handle edge cases with explicit conditionals. Match exact return type.""",
            
            """Generate a mathematically rigorous or algorithmically optimal implementation.
            Use advanced techniques if applicable (e.g., bit manipulation, mathematical identities).
            Include performance considerations. Handle edge cases with mathematical precision."""
        ]

        strategy_context = f"Specification:\n{specification}\n\nDecomposition:\n{str(decomposition)}"
        
        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=strategy_context) for instr in strategy_instructions]
        )

        # PHASE 3: Parallel Code Implementation
        implementations = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Implement the solution based on this strategy:
                {strategy}
                
                Requirements from specification:
                {specification}
                
                Critical: Return EXACTLY the required data type. Handle ALL edge cases from decomposition.
                Include necessary imports inside function if needed. No wrapper code.""",
                context=strategy
            ) for strategy in strategies]
        )

        # PHASE 4: Ensemble Selection
        final_implementation = await self.ensemble(
            instruction="""Select the BEST implementation based on:
            1. Correctness (handles all edge cases from decomposition)
            2. Code quality (readability, efficiency, Pythonic style)
            3. Robustness (type safety, error handling)
            4. Adherence to specification (exact function signature, return type)
            If multiple are excellent, synthesize the best elements into one unified solution.
            Return ONLY the final code implementation with no additional text.""",
            contexts_list=implementations
        )

        # PHASE 5: Iterative Refinement (max 2 iterations)
        current_code = final_implementation
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critically validate this implementation:
                {current_code}
                
                Against specification:
                {specification}
                
                And decomposition:
                {str(decomposition)}
                
                Check:
                1. Does it handle ALL listed edge cases?
                2. Does it return EXACTLY the required data type?
                3. Are imports correctly placed (inside function if needed)?
                4. Is the function signature exactly as required?
                5. Any potential bugs or oversights?
                
                If perfect, respond "VALIDATED". Otherwise, describe specific fixes needed.""",
                context=current_code
            )
            
            if "VALIDATED" in validation.upper():
                break
                
            current_code = await self.revise(
                instruction=f"""Fix the implementation based on this validation feedback:
                {validation}
                
                Maintain exact function signature and return type.
                Preserve the core logic while addressing the issues.
                Return ONLY the corrected code with no additional text.""",
                context=current_code
            )

        return current_code