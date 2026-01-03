# Workflow ID: mbppplus_71_0
# Benchmark: mbppplus
# Data Indices: [327, 328, 214]

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

        # Phase 1: Problem Analysis & Strategy Generation
        analysis = await self.generate(
            instruction="""Thoroughly analyze the programming problem:
            1. Identify input/output types and formats
            2. Infer transformation rules from examples
            3. List potential algorithmic approaches (built-in methods, manual iteration, regex, etc.)
            4. Anticipate edge cases (empty inputs, single elements, boundary values)
            5. Note any type conversion requirements
            6. Consider efficiency constraints
            Present as structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation (3 distinct approaches)
        solution_approaches = [
            "Focus on using built-in Python methods and standard library functions. Prioritize readability and conciseness.",
            "Focus on manual implementation with explicit loops and conditionals. Prioritize educational clarity and step-by-step logic.",
            "Focus on pattern matching and string manipulation techniques (regex, slicing, etc.) where applicable. Prioritize handling format variations."
        ]
        
        initial_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on this analysis:
                {analysis}
                
                Generate a complete Python function implementation using this strategy:
                {approach}
                
                Requirements:
                - Use EXACT function name and signature from problem
                - Handle edge cases explicitly
                - Return correct data type (list, tuple, string, etc.)
                - Include necessary imports inside function if needed
                - Write production-ready, robust code""",
                context=analysis
            ) for approach in solution_approaches]
        )

        # Phase 3: Independent Solution Revision
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically review this solution:
                - Verify it handles ALL edge cases (empty, single element, extremes)
                - Check type consistency (input/output types match requirements)
                - Ensure no off-by-one errors or boundary condition mistakes
                - Confirm efficiency is appropriate for problem scale
                - Fix any logical errors or oversights
                - Preserve original function signature exactly
                Return improved version with fixes applied.""",
                context=sol
            ) for sol in initial_solutions]
        )

        # Phase 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution:
            Criteria in order of priority:
            1. CORRECTNESS: Must handle all edge cases and match expected behavior
            2. ROBUSTNESS: Graceful handling of unexpected inputs
            3. TYPE SAFETY: Returns exactly the required data type
            4. EFFICIENCY: Appropriate algorithmic complexity
            5. READABILITY: Clear, maintainable code
            
            If one solution is clearly superior, select it.
            If multiple have complementary strengths, synthesize a hybrid.
            Return ONLY the final Python function code with imports.""",
            contexts_list=revised_solutions
        )

        # Phase 5: Final Validation Pass
        validated_solution = await self.revise(
            instruction="""Final quality check:
            - Simulate provided test cases mentally
            - Verify function signature is preserved exactly
            - Ensure no placeholder code or TODOs remain
            - Check imports are properly placed (inside function if needed)
            - Confirm output format matches examples exactly
            Return the final polished solution ready for submission.""",
            context=final_solution
        )

        return validated_solution