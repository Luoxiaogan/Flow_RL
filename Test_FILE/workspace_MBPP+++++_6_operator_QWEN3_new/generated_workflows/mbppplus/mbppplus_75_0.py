# Workflow ID: mbppplus_75_0
# Benchmark: mbppplus
# Data Indices: [47, 286]

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

        # Phase 1: Problem Classification & Complexity Assessment
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it based on:
            1. Input/Output Types: What data types are involved? (int, list, string, etc.)
            2. Operation Category: Is it mathematical, logical, structural (data manipulation), or algorithmic?
            3. Complexity Level: Simple (single operation), Medium (multiple steps), Complex (requires decomposition)
            4. Edge Case Indicators: Are there mentions of empty inputs, boundary conditions, or special cases?
            5. Expected Solution Style: Direct computation, transformation, validation, or generation?
            
            Format your response as a structured analysis with clear sections for each category above.
            Be conservative in complexity assessment - if unsure, classify as Medium or Complex.""",
            context=""
        )

        # Phase 2: Strategy Selection based on Classification
        if any(keyword in classification.lower() for keyword in ["simple", "basic", "single operation", "mathematical predicate"]):
            # Direct code generation path for simple problems
            solution = await self.programmer(
                instruction=f"""Generate a Python function that solves the problem exactly as specified.
                Classification context: {classification}
                
                Requirements:
                - Match the exact function signature from the problem
                - Handle all edge cases mentioned or implied
                - Return the correct data type (bool, list, int, etc.)
                - Include necessary imports
                - Code must be production-ready and pass rigorous test suites
                - For mathematical operations, handle negative numbers and zero
                - For collections, handle empty inputs and single elements
                
                Focus on correctness and robustness over performance.""",
                context=classification
            )
        else:
            # Complex path: Decompose and solve
            decomposition = await self.decompose(
                instruction=f"""Break down this programming problem into essential subproblems.
                Problem classification: {classification}
                
                Create 2-5 subproblems that, when solved, will lead to a complete solution.
                Each subproblem should be:
                - Independently solvable
                - Clearly defined with inputs and expected outputs
                - Ordered by logical dependency (if any)
                - Focused on a specific aspect (edge cases, core logic, type handling, etc.)
                
                Format as a numbered list with clear descriptions.""",
                context=classification
            )
            
            # Generate solutions for each subproblem in parallel
            subproblem_solutions = []
            for i, subproblem in enumerate(decomposition):
                if isinstance(subproblem, dict):
                    sub_desc = subproblem.get('description', str(subproblem))
                else:
                    sub_desc = str(subproblem)
                
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem as part of the larger solution:
                    {sub_desc}
                    
                    Context from problem classification: {classification}
                    
                    Requirements:
                    - Provide clear, executable Python code or pseudocode
                    - Handle edge cases specific to this subproblem
                    - Document any assumptions made
                    - Ensure compatibility with other subproblems""",
                    context=classification
                )
                subproblem_solutions.append(sub_solution)
            
            # Synthesize subproblem solutions into final code
            synthesis_context = "\n\n".join([
                f"Subproblem {i+1}: {sol}" 
                for i, sol in enumerate(subproblem_solutions)
            ])
            
            solution = await self.programmer(
                instruction=f"""Synthesize a complete, working solution from these subproblem solutions:
                {synthesis_context}
                
                Original problem classification: {classification}
                
                Requirements:
                - Create a single, cohesive Python function
                - Ensure all subproblem solutions are properly integrated
                - Handle edge cases from all subproblems
                - Match exact function signature and return type
                - Include necessary imports
                - Code must be clean, readable, and production-ready
                - Add comments explaining complex logic if needed""",
                context=synthesis_context
            )

        # Phase 3: Validation and Refinement Loop
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Critically review this solution for potential issues:
                {solution}
                
                Check for:
                1. Edge case handling (empty inputs, boundary values, etc.)
                2. Type consistency (correct return types, parameter types)
                3. Logic errors or off-by-one mistakes
                4. Performance issues (unnecessary complexity)
                5. Readability and maintainability
                
                If no issues found, respond with "VALID: No issues detected".
                If issues found, describe them specifically and suggest fixes.""",
                context=solution
            )
            
            if "VALID:" in validation and "No issues detected" in validation:
                break  # Exit loop if solution is validated
            else:
                solution = await self.revise(
                    instruction=f"""Improve the solution based on this validation feedback:
                    {validation}
                    
                    Requirements:
                    - Fix all identified issues
                    - Maintain correct function signature
                    - Preserve existing functionality while adding robustness
                    - Keep code clean and readable""",
                    context=solution
                )

        # Phase 4: Final Formatting and Output Extraction
        final_output = await self.generate(
            instruction=f"""Extract ONLY the final Python function implementation from this solution:
            {solution}
            
            Rules:
            - Include ONLY the function definition and necessary imports
            - Remove any explanatory text, comments (unless essential for functionality), or markdown formatting
            - Preserve exact function name and parameter names
            - Ensure proper indentation and Python syntax
            - Return as plain text ready for execution
            
            If the solution contains multiple code blocks, select the most complete and correct one.""",
            context=solution
        )

        return final_output