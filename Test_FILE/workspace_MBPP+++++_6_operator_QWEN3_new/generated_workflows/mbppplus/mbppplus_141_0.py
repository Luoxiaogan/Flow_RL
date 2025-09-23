# Workflow ID: mbppplus_141_0
# Benchmark: mbppplus
# Data Indices: [177, 78]

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
        import json
        
        # Phase 1: Problem Classification and Analysis
        classification = await self.generate(
            instruction="""Thoroughly analyze this programming problem. 
            1. Classify the primary operation type (e.g., grouping, indexing, filtering, mathematical, string manipulation, data structure transformation).
            2. Identify key data structures involved (lists, dictionaries, strings, sets, tuples).
            3. Determine expected input/output types and formats.
            4. Predict potential edge cases (empty inputs, single elements, duplicates, boundary conditions, type mismatches).
            5. Assess complexity level (simple, moderate, complex).
            6. Suggest 2-3 possible solution approaches.
            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation and Edge Case Development
        solution_task1 = self.generate(
            instruction=f"""Based on this analysis: {classification}
            Generate a complete, correct Python solution. Focus on:
            - Correctness for all cases including edge cases
            - Proper type handling and return types
            - Clean, readable code
            - Include necessary imports
            - Follow exact function signature from problem
            Provide only the function implementation as specified in requirements.""",
            context=classification
        )
        
        solution_task2 = self.generate(
            instruction=f"""Based on this analysis: {classification}
            Generate an ALTERNATIVE Python solution using a different approach or algorithm. 
            If first solution used built-in functions, use manual implementation. If first was iterative, try recursive.
            Ensure it handles all edge cases identified in analysis.
            Provide only the function implementation as specified in requirements.""",
            context=classification
        )
        
        edge_cases = await self.generate(
            instruction=f"""Based on this analysis: {classification}
            Generate 5 comprehensive edge case test scenarios that would challenge any solution.
            Include: empty inputs, single elements, maximum/minimum values, duplicates, type variations, boundary conditions.
            Format as Python assert statements that could be used for testing.""",
            context=classification
        )

        # Execute parallel tasks
        solutions = await asyncio.gather(solution_task1, solution_task2)
        
        # Phase 3: Solution Validation and Refinement
        validated_solutions = []
        for i, solution in enumerate(solutions):
            try:
                # Test solution with programmer
                test_result = await self.programmer(
                    instruction=f"""Test this solution against edge cases:
                    {edge_cases}
                    
                    Execute the code and verify correctness. If any test fails, note the failure.
                    Return the original code with 'PASSED' or 'FAILED' status and error details if failed.""",
                    context=solution,
                    max_retries=1
                )
                
                if "FAILED" in test_result:
                    # Revise failed solution
                    revised = await self.revise(
                        instruction=f"""The following solution failed testing:
                        {test_result}
                        
                        Revise the code to fix all identified issues while preserving functionality.
                        Ensure it handles all edge cases properly.
                        Return only the corrected function implementation.""",
                        context=solution
                    )
                    validated_solutions.append(revised)
                else:
                    validated_solutions.append(solution)
                    
            except Exception as e:
                # If programmer fails, attempt revision
                revised = await self.revise(
                    instruction=f"""The solution encountered an error during testing: {str(e)}
                    Revise the code to be more robust and handle potential exceptions.
                    Return only the corrected function implementation.""",
                    context=solution
                )
                validated_solutions.append(revised)

        # Phase 4: Solution Synthesis and Finalization
        if len(validated_solutions) > 1:
            final_solution = await self.ensemble(
                instruction="""Evaluate these solutions and select the best one based on:
                1. Correctness (handles all edge cases)
                2. Efficiency (time and space complexity)
                3. Readability and maintainability
                4. Adherence to problem requirements
                5. Robustness against unexpected inputs
                If both are equally good, synthesize a hybrid solution combining their strengths.
                Return ONLY the final function implementation as specified in requirements.""",
                contexts_list=validated_solutions
            )
        else:
            final_solution = validated_solutions[0] if validated_solutions else solutions[0]

        # Phase 5: Final Polish and Type Safety Check
        polished_solution = await self.revise(
            instruction="""Perform final quality check:
            1. Ensure function signature exactly matches problem requirements
            2. Verify return type consistency
            3. Check for any remaining edge cases not handled
            4. Improve variable names and code clarity if needed
            5. Ensure no external dependencies unless necessary
            Return ONLY the final polished function implementation.""",
            context=final_solution
        )

        return polished_solution