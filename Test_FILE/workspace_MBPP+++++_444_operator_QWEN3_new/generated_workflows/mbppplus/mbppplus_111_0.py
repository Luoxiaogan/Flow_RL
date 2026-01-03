# Workflow ID: mbppplus_111_0
# Benchmark: mbppplus
# Data Indices: [28, 185, 148]

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
        
        # Step 1: Problem Classification and Analysis
        classification = await self.generate(
            instruction="""As an expert Python architect, analyze this programming problem systematically:
            1. Examine the function signature - what are the input parameters and expected return type?
            2. Infer the problem category based on naming conventions and parameter types (filtering, searching, sorting, parsing, mathematical, etc.)
            3. Identify likely edge cases (empty inputs, single elements, duplicates, negative numbers, type boundaries)
            4. Determine if order preservation is required
            5. Assess if type conversion is needed
            6. Estimate computational complexity requirements
            Provide a structured analysis with clear categorization and justification.""",
            context=""
        )

        # Step 2: Parallel Solution Generation based on classification
        # Generate multiple solution strategies tailored to the problem type
        solution_strategies = [
            """Implement a direct, straightforward solution using basic Python constructs. 
            Focus on clarity and correctness over optimization. Handle edge cases explicitly.
            Use descriptive variable names and include comments for complex logic.""",
            
            """Implement an optimized solution using appropriate Python built-ins and libraries.
            Consider efficiency for large inputs. Use list comprehensions, generator expressions, 
            or specialized modules when appropriate. Still maintain readability.""",
            
            """Implement a defensive solution with comprehensive error handling and type checking.
            Validate inputs, handle edge cases gracefully, and provide meaningful error messages.
            Prioritize robustness over brevity."""
        ]

        # Generate solutions in parallel
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on the problem classification: {classification}
                
                {strategy}
                
                Implement a complete Python function that solves the problem.
                - Use the exact function signature provided
                - Include necessary imports
                - Handle all identified edge cases
                - Return the correct data type
                - Ensure the solution is self-contained and ready for testing""",
                context=""
            ) for strategy in solution_strategies]
        )

        # Step 3: Solution Validation and Refinement
        refined_solutions = []
        for i, solution in enumerate(solution_attempts):
            refined = await self.revise(
                instruction=f"""Critically review this solution for the problem classified as: {classification}
                
                Validation Checklist:
                1. Does it handle empty inputs correctly?
                2. Does it handle single element cases?
                3. Does it handle duplicates appropriately?
                4. Does it handle negative numbers and zero?
                5. Does it return the correct data type?
                6. Is the solution efficient for large inputs?
                7. Are there any boundary condition issues?
                8. Does it match the expected behavior from the problem description?
                
                Improve the solution by fixing any identified issues.
                If no issues are found, enhance clarity and add comments explaining edge case handling.
                Maintain the original approach unless fundamental flaws are discovered.""",
                context=solution
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Selection - Choose the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates based on these criteria:
            1. Correctness: Handles all edge cases and produces correct output
            2. Efficiency: Optimal time and space complexity for the problem
            3. Readability: Clear, well-structured code with appropriate comments
            4. Robustness: Graceful handling of unexpected inputs
            5. Simplicity: Avoids unnecessary complexity while maintaining correctness
            
            If multiple solutions are equally good, prefer the most readable and maintainable.
            The selected solution must be production-ready and pass all test cases including edge cases.
            Return only the final Python code with no additional explanation.""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Validation and Formatting
        validated_solution = await self.revise(
            instruction="""Perform final quality assurance on the selected solution:
            1. Verify the function signature matches exactly what was requested
            2. Ensure all necessary imports are included at the top
            3. Check that return types are correct
            4. Confirm edge case handling is comprehensive
            5. Format the code according to PEP 8 guidelines
            6. Remove any debug statements or unnecessary comments
            7. Ensure the solution is self-contained and ready for immediate testing
            
            Return only the final, polished Python code with no additional text.""",
            context=final_solution
        )

        return validated_solution