# Workflow ID: mbppplus_72_0
# Benchmark: mbppplus
# Data Indices: [155, 22]

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
        Universal workflow for programming problem domain.
        Dynamically adapts strategy based on problem characteristics.
        """
        import asyncio
        import re
        import json

        # Phase 1: Parallel Problem Classification
        classification_tasks = [
            self.generate(
                instruction="""Analyze this programming problem from an ALGORITHMIC perspective:
                - What type of algorithm is needed? (string processing, mathematical, data structure, etc.)
                - What are the key operations? (searching, sorting, transforming, matching, etc.)
                - What data structures are involved? (lists, strings, sets, etc.)
                - Are there any special constraints or edge cases mentioned?
                Provide a structured analysis focusing on algorithmic requirements.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a MATHEMATICAL/LOGICAL perspective:
                - Are there mathematical operations or formulas needed?
                - What logical conditions must be satisfied?
                - Are there numerical patterns or sequences involved?
                - What are the boundary conditions and edge cases?
                Provide a structured analysis focusing on mathematical/logical requirements.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a STRUCTURAL/FORMAT perspective:
                - What is the exact function signature required?
                - What are the input and output data types?
                - Are there specific format requirements for the output?
                - What edge cases related to data structure (empty inputs, single elements, etc.) should be considered?
                Provide a structured analysis focusing on structural and format requirements.""",
                context=""
            )
        ]
        
        classifications = await asyncio.gather(*classification_tasks)
        
        # Synthesize classifications into unified problem understanding
        problem_analysis = await self.ensemble(
            instruction="""Synthesize the three analyses into a comprehensive problem understanding:
            1. Combine algorithmic, mathematical, and structural insights
            2. Identify the primary problem category and required approach
            3. Extract key requirements for solution implementation
            4. List critical edge cases and format constraints
            5. Determine if this is primarily a string, mathematical, or data structure problem
            Provide a clear, structured summary that will guide solution generation.""",
            contexts_list=classifications
        )

        # Phase 2: Generate multiple solution candidates in parallel
        solution_tasks = [
            self.programmer(
                instruction=f"""Generate a Python solution focusing on CORRECTNESS and EDGE CASES:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Handle all edge cases identified in analysis
                - Follow exact function signature from problem
                - Return correct data types as specified
                - Include necessary imports inside function if needed
                - Prioritize robustness over performance
                Generate complete, executable code that solves the problem correctly.""",
                context=problem_analysis
            ),
            self.programmer(
                instruction=f"""Generate a Python solution focusing on PERFORMANCE and EFFICIENCY:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Optimize for computational efficiency
                - Use appropriate data structures and algorithms
                - Minimize unnecessary operations
                - Still handle critical edge cases
                - Follow exact function signature from problem
                Generate complete, executable code that solves the problem efficiently.""",
                context=problem_analysis
            ),
            self.programmer(
                instruction=f"""Generate a Python solution focusing on READABILITY and MAINTAINABILITY:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Use clear, descriptive variable names
                - Include helpful comments explaining logic
                - Structure code for easy understanding
                - Follow exact function signature from problem
                - Handle obvious edge cases
                Generate complete, executable code that is easy to understand and maintain.""",
                context=problem_analysis
            )
        ]
        
        solution_candidates = await asyncio.gather(*solution_tasks)

        # Phase 3: Validate and refine solutions
        best_solution = None
        validation_results = []
        
        for i, candidate in enumerate(solution_candidates):
            # Validate each candidate
            validation = await self.revise(
                instruction=f"""Critically evaluate this solution candidate:
                - Does it handle all edge cases from problem analysis?
                - Does it follow the exact function signature and return types?
                - Are there any logical errors or boundary condition issues?
                - Is the code safe and free from potential errors?
                - Does it match the problem requirements exactly?
                
                Problem Analysis: {problem_analysis}
                
                If issues are found, provide specific fixes. If no issues, confirm it's ready for use.
                Format your response as: "VALIDATION: [status] - [detailed feedback]" where status is either "PASS" or "FAIL".""",
                context=candidate
            )
            
            validation_results.append(validation)
            
            # If this is the first passing solution, use it as baseline
            if "VALIDATION: PASS" in validation and best_solution is None:
                best_solution = candidate

        # If no solution passed validation, use ensemble to select best candidate
        if best_solution is None:
            best_solution = await self.ensemble(
                instruction="""Select the best solution from among the candidates:
                - Consider which solution has the fewest critical issues
                - Prioritize solutions that handle edge cases correctly
                - Consider code quality and adherence to requirements
                - If all have issues, select the one easiest to fix
                Return only the selected solution code, nothing else.""",
                contexts_list=solution_candidates
            )

        # Phase 4: Final refinement and format compliance check
        final_solution = await self.revise(
            instruction=f"""Final refinement of solution:
            - Ensure exact function name and signature from original problem
            - Verify return types match requirements exactly
            - Check for any remaining edge cases
            - Remove any unnecessary code or comments
            - Ensure imports are included if needed (inside function)
            - Format code cleanly and consistently
            - Output ONLY the function implementation, nothing else
            
            Problem Analysis: {problem_analysis}""",
            context=best_solution
        )

        # Phase 5: Generate test cases for self-validation (if needed)
        # This step creates additional test cases to verify solution robustness
        test_validation = await self.programmer(
            instruction=f"""Generate 3-5 additional test cases that verify edge cases:
            - Include empty inputs, boundary values, and special cases
            - Format as assert statements
            - Test the solution against these cases
            - If any fail, suggest fixes
            
            Solution to test: {final_solution}
            
            Problem Analysis: {problem_analysis}
            
            Return either "ALL TESTS PASS" or specific fixes needed.""",
            context=final_solution
        )

        # If test validation fails, do one final revision
        if "ALL TESTS PASS" not in test_validation:
            final_solution = await self.revise(
                instruction=f"""Apply these fixes to make the solution pass all tests:
                Test Feedback: {test_validation}
                
                Requirements:
                - Keep function signature identical
                - Fix only the issues identified
                - Maintain code quality
                - Output ONLY the function implementation
                
                Problem Analysis: {problem_analysis}""",
                context=final_solution
            )

        return final_solution