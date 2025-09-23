# Workflow ID: mbppplus_103_0
# Benchmark: mbppplus
# Data Indices: [274, 34, 345]

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

        # Phase 1: Parallel problem analysis from multiple perspectives
        analysis_instructions = [
            """Analyze this programming problem with extreme precision. Focus on:
            1. Exact input and output types (list, tuple, set, string, etc.)
            2. Function signature requirements and parameter meanings
            3. Edge cases (empty inputs, single elements, duplicates, negatives)
            4. Algorithmic patterns this resembles (sorting, searching, transforming)
            5. Potential pitfalls and common mistakes
            6. Required imports and Python idioms
            Provide a structured, detailed analysis that could guide implementation.""",
            
            """Approach this problem from first principles. Ignore any reference solution.
            1. What is the core computational task being asked?
            2. What are the minimal assumptions needed to solve it?
            3. What would a naive solution look like? What would an optimized one look like?
            4. What test cases would you design to verify correctness?
            5. What are the boundary conditions and special cases?
            Think like a computer scientist designing from scratch.""",
            
            """Analyze this problem by analogy. 
            1. What similar problems have you seen before?
            2. What standard library functions or modules could help?
            3. What data structures are most appropriate?
            4. How would you explain this problem to a junior developer?
            5. What are the performance implications of different approaches?
            Draw connections to known patterns and solutions."""
        ]

        # Generate parallel analyses
        analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in analysis_instructions]
        )

        # Summarize each analysis to extract core insights
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Extract the 3-5 most critical insights that would guide implementation. Focus on requirements, edge cases, and algorithmic approach.",
                context=analysis
            ) for analysis in analyses]
        )

        # Phase 2: Ensemble the analyses into unified solution strategy
        solution_strategy = await self.ensemble(
            instruction="""Synthesize these analyses into a single, coherent solution strategy. Consider:
            1. What is the consensus on input/output types and function signature?
            2. What edge cases must be handled?
            3. What is the recommended algorithmic approach?
            4. What imports or Python features are needed?
            5. What are the key implementation steps?
            Resolve contradictions by favoring the most conservative, robust interpretation.
            Output a clear, step-by-step implementation plan.""",
            contexts_list=summaries
        )

        # Phase 3: Generate initial implementation
        initial_implementation = await self.generate(
            instruction=f"""Implement the solution according to this strategy:
            {solution_strategy}
            
            Requirements:
            1. Use the EXACT function name and signature from the problem
            2. Include ALL necessary imports at the top
            3. Handle ALL edge cases mentioned in the strategy
            4. Return the correct data type (list, tuple, set, etc.)
            5. Write clean, readable, Pythonic code
            6. Do NOT include any test cases or print statements
            7. Do NOT wrap in any outer function or class
            
            Output ONLY the function implementation in this format:
            # imports
            def function_name(params):
                # implementation
                return result""",
            context=solution_strategy
        )

        # Phase 4: Self-critique and revision
        critique = await self.generate(
            instruction="""Critically review this implementation:
            1. Does it handle empty inputs? Single elements? Duplicates?
            2. Are return types correct? Are imports complete?
            3. Could it fail on any edge cases? What are they?
            4. Is the logic correct for all possible inputs?
            5. Are there any Python anti-patterns or inefficiencies?
            6. Does it match the function signature exactly?
            Be brutally honest. List specific issues and improvements needed.""",
            context=initial_implementation
        )

        # Revise based on critique
        revised_implementation = await self.revise(
            instruction="""Revise this implementation to fix all identified issues:
            1. Address every critique point specifically
            2. Maintain exact function signature
            3. Ensure all edge cases are handled
            4. Keep code clean and readable
            5. Verify return types and imports
            6. Output ONLY the function implementation in required format""",
            context=f"Original implementation:\n{initial_implementation}\n\nCritique:\n{critique}"
        )

        # Phase 5: Final compliance check and formatting
        final_output = await self.revise(
            instruction="""Ensure this code meets ALL requirements:
            1. Starts with necessary imports (if any)
            2. Uses EXACT function name from problem
            3. Has correct parameter names and order
            4. Returns appropriate data type
            5. Handles edge cases (empty, single element, etc.)
            6. No extra text, comments, or wrappers
            7. Clean, idiomatic Python
            
            If any requirement is not met, fix it. Output ONLY the function implementation.""",
            context=revised_implementation
        )

        # Extract just the code block if it's wrapped in markdown
        code_match = re.search(r'