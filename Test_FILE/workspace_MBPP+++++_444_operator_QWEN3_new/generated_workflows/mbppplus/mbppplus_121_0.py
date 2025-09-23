# Workflow ID: mbppplus_121_0
# Benchmark: mbppplus
# Data Indices: [50, 307, 32]

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

        # Phase 1: Deep problem analysis - extract intent, edge cases, constraints
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:
            1. Core task: What is the function supposed to compute or determine?
            2. Input specifications: What are the expected data types, structures, and constraints?
            3. Output requirements: What should be returned, and in what format?
            4. Edge cases: List at least 5 potential edge cases (empty inputs, single elements, duplicates, type mismatches, boundary values)
            5. Performance considerations: Are there implied efficiency requirements?
            6. Hidden assumptions: What unstated conditions might affect correctness?
            7. Validation criteria: What would constitute a 'correct' solution beyond basic functionality?
            Present your analysis in structured markdown with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel solution generation under different strategic lenses
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution that prioritizes CORRECTNESS and EDGE-CASE HANDLING above all else.
                Use the following analysis context:
                {problem_analysis}
                
                Requirements:
                - Handle all edge cases mentioned in the analysis explicitly
                - Include input validation and type checking where appropriate
                - Use defensive programming patterns
                - Prefer clarity and robustness over conciseness
                - Return exactly the required data type (list, tuple, int, etc.)
                - Include necessary imports inside the function if needed
                Output ONLY the function implementation with no additional text.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution that prioritizes COMPUTATIONAL EFFICIENCY and ELEGANCE.
                Use the following analysis context:
                {problem_analysis}
                
                Requirements:
                - Optimize for time/space complexity where possible
                - Use appropriate data structures and algorithms
                - Avoid unnecessary operations or redundant checks
                - Still handle critical edge cases (empty, single element)
                - Return exactly the required data type
                - Include necessary imports inside the function if needed
                Output ONLY the function implementation with no additional text.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution that prioritizes READABILITY and EDUCATIONAL VALUE.
                Use the following analysis context:
                {problem_analysis}
                
                Requirements:
                - Use clear, descriptive variable names
                - Include brief inline comments explaining key steps
                - Structure code for easy understanding
                - Handle obvious edge cases
                - Return exactly the required data type
                - Include necessary imports inside the function if needed
                Output ONLY the function implementation with no additional text.""",
                context=problem_analysis
            )
        )

        # Phase 3: Stress-test each candidate against edge cases
        validated_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"""STRESS TEST AND HARDEN THIS SOLUTION:
                1. Review the original problem analysis for edge cases and constraints
                2. Modify this solution to explicitly handle ALL identified edge cases
                3. Add input validation if not present
                4. Ensure type consistency in returns
                5. If any edge case cannot be handled, document it with a comment
                6. Preserve the core logic but make it bulletproof
                Return ONLY the revised function implementation.""",
                context=candidate
            ) for candidate in solution_candidates]
        )

        # Phase 4: Ensemble synthesis - combine the best elements
        final_solution = await self.ensemble(
            instruction="""SYNTHESIZE THE ULTIMATE SOLUTION:
            You are given multiple candidate solutions for the same problem.
            Your task is to create the most robust, correct, and production-ready version by:
            1. Taking the most comprehensive edge-case handling from any candidate
            2. Preserving computational efficiency where possible
            3. Maintaining readability through clear structure
            4. Ensuring strict type compliance with return requirements
            5. Removing any redundant or conflicting code
            6. Adding minimal necessary imports inside the function
            7. Outputting ONLY the final function implementation with exact signature
            
            CRITICAL: The solution must handle empty inputs, type edge cases, and boundary conditions explicitly.
            When in doubt, choose the most defensive programming approach.""",
            contexts_list=validated_candidates
        )

        # Phase 5: Final formatting and compliance check
        cleaned_solution = await self.summarize(
            instruction="""FINAL COMPLIANCE CHECK AND FORMATTING:
            Extract ONLY the function implementation from the provided text.
            Requirements:
            - Must start with 'def function_name(...):' exactly as specified
            - Must include any necessary imports inside the function body
            - Must return the correct data type (int, bool, list, tuple, etc.)
            - Must contain no explanatory text, comments, or markdown
            - Must be syntactically valid Python code
            If any requirements are not met, fix them before returning.
            Return ONLY the cleaned function code.""",
            context=final_solution
        )

        return cleaned_solution