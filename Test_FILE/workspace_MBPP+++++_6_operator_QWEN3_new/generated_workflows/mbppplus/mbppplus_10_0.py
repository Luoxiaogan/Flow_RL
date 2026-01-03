# Workflow ID: mbppplus_10_0
# Benchmark: mbppplus
# Data Indices: [236, 95]

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

        # Step 1: Decompose the problem to understand its structure and requirements
        decomposition = await self.decompose(
            instruction="""Thoroughly analyze this programming problem and break it down into its fundamental components. For each component, provide:
            1. Input types and structures (lists, tuples, numbers, strings, etc.)
            2. Output requirements (exact type, format, and structure expected)
            3. Core algorithmic operation needed (mathematical computation, data transformation, searching, etc.)
            4. Edge cases to consider (empty inputs, single elements, boundary values, type variations)
            5. Any implicit constraints or assumptions
            6. Classification of problem type (mathematical, data structure, string manipulation, etc.)
            Present this as a structured analysis that can guide solution generation.""",
            context=""
        )

        # Convert decomposition list to string for context passing
        decomposition_text = "\n".join([f"{item['id']}: {item['description']}" for item in decomposition])

        # Step 2: Generate multiple solution approaches in parallel
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this problem decomposition:
                {decomposition_text}
                
                Generate a solution using a mathematical/formulaic approach. Focus on deriving closed-form expressions or mathematical patterns. 
                Include clear variable definitions and show the mathematical reasoning. This approach is best for problems involving sequences, 
                series, or arithmetic patterns. Return only the Python function implementation with proper signature.""",
                context=decomposition_text
            ),
            self.generate(
                instruction=f"""Based on this problem decomposition:
                {decomposition_text}
                
                Generate a solution using an iterative/procedural approach. Use explicit loops and step-by-step operations. 
                This approach is robust and handles edge cases well. Focus on clarity and correctness over elegance. 
                Include comments explaining key steps. Return only the Python function implementation with proper signature.""",
                context=decomposition_text
            ),
            self.generate(
                instruction=f"""Based on this problem decomposition:
                {decomposition_text}
                
                Generate a solution using a functional/data-transformation approach. Leverage Python's built-in functions, 
                list comprehensions, or functional programming concepts. This approach is ideal for data structure manipulation problems. 
                Focus on clean, concise code. Return only the Python function implementation with proper signature.""",
                context=decomposition_text
            )
        )

        # Step 3: Ensemble the solutions - synthesize the best elements from each
        synthesized_solution = await self.ensemble(
            instruction="""You have three different solution approaches to the same programming problem. 
            Your task is to synthesize the best solution by:
            1. Identifying which approach is most correct and handles edge cases best
            2. Incorporating strengths from other approaches where they improve robustness or efficiency
            3. Ensuring the solution matches the exact function signature and return type required
            4. Preserving clarity and maintainability
            5. Adding comments only if they significantly improve understanding
            Return only the final Python function implementation - no explanations or markdown.""",
            contexts_list=solution_approaches
        )

        # Step 4: Validate the solution against edge cases identified in decomposition
        validation_result = await self.programmer(
            instruction=f"""Test the following solution against edge cases. The edge cases to test are:
            {decomposition_text}
            
            Execute the code with these test cases. If any fail, return the specific input that failed and the error message.
            If all pass, return 'VALIDATED'. Do not attempt to fix the code - only report validation results.""",
            context=synthesized_solution,
            max_retries=1
        )

        # Step 5: Revise if validation fails
        current_solution = synthesized_solution
        if "VALIDATED" not in validation_result:
            for attempt in range(2):  # Allow up to 2 revisions
                revised_solution = await self.revise(
                    instruction=f"""The following solution failed validation:
                    Validation result: {validation_result}
                    
                    Diagnose the specific failure. Was it:
                    - Logic error in algorithm?
                    - Type mismatch or incorrect return type?
                    - Unhandled edge case?
                    - Off-by-one error?
                    - Performance issue?
                    
                    Revise the solution to fix these specific issues while preserving the core approach unless fundamentally flawed.
                    Ensure the function signature remains exactly as required. Return only the revised Python function implementation.""",
                    context=current_solution
                )
                current_solution = revised_solution
                
                # Re-validate
                validation_result = await self.programmer(
                    instruction=f"""Re-test the revised solution against edge cases:
                    {decomposition_text}
                    
                    Execute the code with these test cases. If any fail, return the specific input that failed and the error message.
                    If all pass, return 'VALIDATED'. Do not attempt to fix the code - only report validation results.""",
                    context=current_solution,
                    max_retries=1
                )
                
                if "VALIDATED" in validation_result:
                    break

        # Step 6: Final cleanup and formatting
        final_solution = await self.summarize(
            instruction="""Extract only the Python function implementation from the text below. 
            Ensure it has:
            - Exact function name and parameters as specified in the original problem
            - All necessary imports at the top (if any)
            - Proper return type and structure
            - No additional text, explanations, or markdown formatting
            - Preserve all whitespace and indentation exactly as required for valid Python code
            Return only the clean function implementation.""",
            context=current_solution
        )

        return final_solution