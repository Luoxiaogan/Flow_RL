# Workflow ID: mbppplus_50_0
# Benchmark: mbppplus
# Data Indices: [225, 210]

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
        import json

        # Step 1: Classify the problem type and extract key requirements
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth and classify it into one of these categories:
            1. STRUCTURAL COMPARISON - Problems that involve comparing data structures for equality or similarity (e.g., lists, tuples, sets)
            2. MATHEMATICAL COMPUTATION - Problems requiring arithmetic, geometric, or algebraic calculations
            3. ALGORITHMIC TRANSFORMATION - Problems requiring data processing, filtering, mapping, or reduction
            4. LOGICAL VALIDATION - Problems requiring conditional logic, validation, or decision trees
            
            For each category, explain why it fits or doesn't fit. Identify:
            - Key operations needed (comparison, calculation, iteration, etc.)
            - Expected edge cases (empty inputs, zeros, negatives, duplicates, etc.)
            - Required output format and data types
            - Potential pitfalls or common mistakes
            
            Finally, recommend the most appropriate solution strategy and estimate complexity (1-5 scale).""",
            context=""
        )

        # Step 2: Determine complexity and decide on single vs. parallel solution generation
        complexity_analysis = await self.generate(
            instruction="""Based on the classification below, assign a complexity score (1-5) where:
            1 = Trivial (direct comparison or single operation)
            2 = Simple (few operations, obvious edge cases)
            3 = Moderate (multiple steps, several edge cases)
            4 = Complex (nested logic, many edge cases)
            5 = Very Complex (algorithmic, mathematical proofs, etc.)
            
            Justify your score. Then decide: should we generate one solution or multiple parallel solutions?
            For complexity <= 2: single solution
            For complexity > 2: generate 2-3 different solution approaches in parallel
            
            Classification:
            """ + classification,
            context=classification
        )

        # Step 3: Generate solution(s) based on complexity
        if "single solution" in complexity_analysis.lower() or "complexity <= 2" in complexity_analysis.lower():
            # Generate single solution
            solution_attempt = await self.programmer(
                instruction=f"""Generate Python code that solves the problem. Follow these strict rules:
                - Output ONLY the function implementation with exact signature from problem
                - Include necessary imports inside the function if needed
                - Handle ALL edge cases: empty inputs, zeros, negatives, duplicates, boundary values
                - Return correct data type as specified
                - Code must be robust, efficient, and readable
                - Include internal validation for edge cases using assertions
                
                Problem classification and requirements:
                {classification}
                
                If code fails any internal assertion, revise and fix immediately.""",
                context=classification,
                max_retries=3
            )
            candidate_solutions = [solution_attempt]
        else:
            # Generate multiple solutions in parallel
            solution_promises = []
            for i in range(3):  # Generate 3 different approaches
                solution_promises.append(
                    self.programmer(
                        instruction=f"""Generate Python code that solves the problem using a DIFFERENT approach than other solutions. 
                        Approach {i+1} should use a unique strategy or algorithm. Follow these strict rules:
                        - Output ONLY the function implementation with exact signature from problem
                        - Include necessary imports inside the function if needed
                        - Handle ALL edge cases: empty inputs, zeros, negatives, duplicates, boundary values
                        - Return correct data type as specified
                        - Code must be robust, efficient, and readable
                        - Include internal validation for edge cases using assertions
                        
                        Problem classification and requirements:
                        {classification}
                        
                        If code fails any internal assertion, revise and fix immediately.""",
                        context=classification,
                        max_retries=3
                    )
                )
            candidate_solutions = await asyncio.gather(*solution_promises)

        # Step 4: Ensemble - select best solution or synthesize
        if len(candidate_solutions) == 1:
            final_solution = candidate_solutions[0]
        else:
            final_solution = await self.ensemble(
                instruction="""Evaluate all candidate solutions and select the BEST one based on:
                1. Correctness - passes all edge case validations
                2. Robustness - handles all specified edge cases gracefully
                3. Readability - clean, well-structured code
                4. Efficiency - optimal time/space complexity
                5. Simplicity - avoids unnecessary complexity
                
                If multiple solutions are equally good, synthesize them into a hybrid solution that combines their strengths.
                Output ONLY the final function implementation - no explanations, no markdown, no additional text.""",
                contexts_list=candidate_solutions
            )

        # Step 5: Final validation and cleanup
        cleaned_solution = await self.revise(
            instruction="""Clean and finalize the solution:
            - Ensure ONLY the function implementation is present (no extra text, markdown, or explanations)
            - Verify function signature matches exactly (name, parameters)
            - Confirm all necessary imports are included inside the function if needed
            - Remove any test cases, print statements, or debug code
            - Ensure proper indentation and Python syntax
            - Return the clean, production-ready code""",
            context=final_solution
        )

        return cleaned_solution