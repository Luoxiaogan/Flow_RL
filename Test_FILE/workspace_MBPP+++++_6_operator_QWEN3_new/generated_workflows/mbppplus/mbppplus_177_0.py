# Workflow ID: mbppplus_177_0
# Benchmark: mbppplus
# Data Indices: [182, 111]

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

        # Phase 1: Meta-Analysis - Understand problem type and requirements
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis. Classify along these dimensions:
            1. Problem Type: Mathematical, Data Structure, String Manipulation, Logical, or Hybrid
            2. Input/Output: What data types are involved? Are there type conversion requirements?
            3. Order Sensitivity: Must original order be preserved? 
            4. Edge Cases: What edge cases are implied? (empty inputs, single elements, duplicates, boundaries)
            5. Computational Approach: Formula-based, Iterative, Recursive, or Set-based?
            6. Validation Needs: Are there hidden constraints or precision requirements?
            7. Complexity: Single-step or multi-step with dependencies?
            Provide structured analysis with clear labels for each dimension.""",
            context=""
        )

        # Phase 2: Strategy Generation - Create multiple solution approaches
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on analysis: {problem_analysis}
                Generate a solution focusing on MATHEMATICAL PRECISION and formula correctness.
                Include detailed comments explaining each computational step.
                Handle edge cases explicitly in code.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on analysis: {problem_analysis}
                Generate a solution focusing on READABILITY and maintainability.
                Use clear variable names and step-by-step logic.
                Include comprehensive edge case handling.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on analysis: {problem_analysis}
                Generate a solution focusing on PERFORMANCE and efficiency.
                Optimize for time/space complexity.
                Include complexity analysis in comments.""",
                context=problem_analysis
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Selection - Choose best approach based on problem requirements
        selected_strategy = await self.ensemble(
            instruction=f"""Select the best solution strategy based on:
            - Alignment with problem type identified in analysis: {problem_analysis}
            - Completeness of edge case handling
            - Correctness of computational approach
            - Code clarity and maintainability
            - Efficiency where relevant
            Return ONLY the selected solution code with no additional text.""",
            contexts_list=strategy_candidates
        )

        # Phase 4: Implementation Validation - Test against edge cases
        validation_context = await self.generate(
            instruction=f"""Generate 5 comprehensive test cases including:
            1. Typical case
            2. Empty input case
            3. Single element case  
            4. Boundary value case
            5. Duplicate/edge case specific to problem
            Format as Python assert statements.""",
            context=problem_analysis
        )

        # Phase 5: Iterative Refinement Loop
        current_solution = selected_strategy
        for iteration in range(3):
            try:
                # Attempt to execute solution with validation tests
                execution_result = await self.programmer(
                    instruction=f"""Implement the function exactly as specified.
                    Validate against these test cases:
                    {validation_context}
                    Return ONLY the final working code with no additional text.""",
                    context=current_solution,
                    max_retries=1
                )
                
                # Check if execution was successful (no error markers)
                if "error" not in execution_result.lower() and "exception" not in execution_result.lower():
                    current_solution = execution_result
                    break
                else:
                    # Generate specific fixes based on error
                    fix_instruction = await self.generate(
                        instruction=f"""Analyze this failed implementation:
                        {execution_result}
                        
                        Generate specific fixes for the errors encountered.
                        Focus on the test cases that failed.
                        Provide revised code that addresses these issues.""",
                        context=current_solution
                    )
                    current_solution = await self.revise(
                        instruction="Incorporate fixes while preserving core logic",
                        context=fix_instruction
                    )
            except Exception as e:
                # Fallback revision on exception
                current_solution = await self.revise(
                    instruction=f"Fix implementation errors. Last error: {str(e)}",
                    context=current_solution
                )

        # Phase 6: Final Polishing - Ensure clean, compliant output
        final_solution = await self.summarize(
            instruction="""Extract ONLY the function implementation from the solution.
            Ensure it matches EXACTLY the required signature from the problem.
            Remove any test code, print statements, or extra text.
            Return ONLY the function definition with imports if needed.""",
            context=current_solution
        )

        return final_solution