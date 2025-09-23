# Workflow ID: mbppplus_55_0
# Benchmark: mbppplus
# Data Indices: [188, 238, 100]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Comprehensive problem analysis
        analysis = await self.generate(
            instruction="""Perform deep problem analysis. Answer these questions:
            1. What category does this problem belong to? (mathematical, data structure, string manipulation, etc.)
            2. What are the input types and expected output types?
            3. What edge cases must be handled? (empty inputs, single elements, boundary values, type mismatches)
            4. What algorithmic approaches are suitable? (brute force, greedy, dynamic programming, etc.)
            5. What are the efficiency requirements? (time/space complexity)
            6. Are there any hidden constraints or assumptions?
            7. What would cause a solution to fail in production?
            Provide detailed, structured analysis covering all these points.""",
            context=""
        )

        # Step 2: Summarize analysis into compact specification
        spec = await self.summarize(
            instruction="""Extract and condense the most critical constraints and requirements from the analysis.
            Format as bullet points:
            - Category: [problem category]
            - Input: [input types and constraints]
            - Output: [output type and format]
            - Edge Cases: [list of critical edge cases]
            - Efficiency: [required complexity]
            - Failure Modes: [what must be avoided]
            Keep it concise but comprehensive - this will guide all subsequent steps.""",
            context=analysis
        )

        # Step 3: Generate multiple solution approaches in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using the most straightforward approach.
                Specifications:
                {spec}
                
                Write clean, readable code that handles all edge cases mentioned above.
                Include necessary imports. Follow exact function signature from problem.
                Output ONLY the function implementation, no explanations.""",
                context=spec
            ),
            self.generate(
                instruction=f"""Generate a solution using an optimized/alternative approach.
                Specifications:
                {spec}
                
                Consider efficiency improvements, clever data structures, or mathematical insights.
                Write production-ready code that handles all edge cases.
                Include necessary imports. Follow exact function signature.
                Output ONLY the function implementation, no explanations.""",
                context=spec
            ),
            self.generate(
                instruction=f"""Generate a defensive programming solution that prioritizes robustness.
                Specifications:
                {spec}
                
                Add explicit type checks, input validation, and error handling where appropriate.
                Ensure graceful handling of all edge cases.
                Include necessary imports. Follow exact function signature.
                Output ONLY the function implementation, no explanations.""",
                context=spec
            )
        )

        # Step 4: Generate synthetic edge case tests for validation
        edge_cases = await self.generate(
            instruction=f"""Generate 5-7 synthetic test cases that would expose common bugs.
            Specifications:
            {spec}
            
            Focus on:
            - Boundary conditions
            - Empty or minimal inputs
            - Type edge cases
            - Performance stress tests
            - Invalid inputs (if applicable)
            
            Format as Python assert statements that should pass for a correct solution.
            Only output the assert statements, one per line.""",
            context=spec
        )

        # Step 5: Validate each solution against synthetic edge cases
        validation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate this solution against the edge case tests:
                Solution:
                {solution}
                
                Edge Cases:
                {edge_cases}
                
                Analyze: Does this solution pass all edge cases? If not, what fails and why?
                Be specific about bugs, edge case handling, and potential improvements.
                Also evaluate code quality, efficiency, and adherence to specifications.
                Provide detailed critique with line numbers if possible.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 6: Ensemble - select best solution based on validation
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on:
            1. Correctness (passes all edge cases)
            2. Efficiency (meets complexity requirements)
            3. Robustness (handles edge cases gracefully)
            4. Code quality (readability, maintainability)
            5. Adherence to specifications
            
            Here are the solutions and their validation critiques:
            {list(zip(solution_attempts, validation_results))}
            
            Choose the single best solution. If multiple are equally good, prefer the most efficient.
            Output ONLY the selected solution code, nothing else.""",
            contexts_list=solution_attempts
        )

        # Step 7: Targeted revision based on validation feedback
        refined_solution = await self.revise(
            instruction=f"""Refine this solution based on the validation feedback:
            Solution:
            {best_solution}
            
            Validation Feedback:
            {validation_results[solution_attempts.index(best_solution)] if best_solution in solution_attempts else "No specific feedback"}
            
            Specifications:
            {spec}
            
            Fix any identified bugs or weaknesses. Improve code quality if needed.
            Ensure perfect handling of all edge cases. Optimize if possible.
            Maintain exact function signature and output format.
            Output ONLY the final function implementation, no explanations or markdown.""",
            context=best_solution
        )

        # Step 8: Final extraction and cleanup (ensure pure code output)
        code_extraction = await self.generate(
            instruction="""Extract ONLY the Python function code from the following text.
            Remove any explanations, markdown formatting, or additional text.
            The output must be pure Python code that can be executed directly.
            Preserve all imports, function signature, and indentation exactly.
            If no code is found, return an empty string.""",
            context=refined_solution
        )

        # Clean up any remaining markdown or extra text
        final_code = code_extraction.strip()
        if final_code.startswith("