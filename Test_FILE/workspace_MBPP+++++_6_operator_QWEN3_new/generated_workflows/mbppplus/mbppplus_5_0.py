# Workflow ID: mbppplus_5_0
# Benchmark: mbppplus
# Data Indices: [107, 60]

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

        # STEP 1: CLASSIFY PROBLEM & ESTIMATE COMPLEXITY
        classification = await self.generate(
            instruction="""Analyze the problem and classify it with high precision:
            1. Problem Category: Is it string manipulation, mathematical computation, list/tuple operation, data structure algorithm, or logic problem?
            2. Complexity Level: Simple (direct transformation), Medium (requires iteration or conditionals), Complex (requires DP, recursion, or multi-step reasoning)
            3. Key Operations: What core operations are needed? (e.g., splitting, summing, filtering, sorting)
            4. Edge Cases: What edge cases must be handled? (empty inputs, single elements, duplicates, type boundaries)
            5. Output Format: What exact return type is required? (list, tuple, int, etc.)
            6. Confidence Score: Rate your classification confidence 1-10.
            Format as a structured JSON-like response with clear sections.""",
            context=""
        )

        # STEP 2: CONDITIONAL ROUTING BASED ON COMPLEXITY
        if "Simple" in classification and "Confidence Score: 8" in classification or "Confidence Score: 9" in classification or "Confidence Score: 10" in classification:
            # Direct path for high-confidence simple problems
            solution_draft = await self.generate(
                instruction=f"""Generate a direct, clean Python function solution based on this classification:
                {classification}
                
                Requirements:
                - Match the exact function signature from the problem
                - Handle all edge cases mentioned in classification
                - Include necessary imports
                - Return correct data type
                - No extra text or explanations — only code
                - Prioritize readability and efficiency""",
                context=classification
            )
        else:
            # Complex path: Parallel strategy generation + decomposition
            strategy_promises = [
                self.generate(
                    instruction=f"""Propose Strategy A: Solve using iterative approach
                    Classification context: {classification}
                    - Detail step-by-step logic
                    - Identify variables and state tracking needed
                    - Specify edge case handling
                    - Outline code structure""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Propose Strategy B: Solve using functional/declarative approach
                    Classification context: {classification}
                    - Detail step-by-step logic
                    - Identify transformations and mappings
                    - Specify edge case handling
                    - Outline code structure""",
                    context=classification
                )
            ]
            
            if "Complex" in classification:
                strategy_promises.append(
                    self.generate(
                        instruction=f"""Propose Strategy C: Solve using dynamic programming or recursive approach
                        Classification context: {classification}
                        - Detail state transitions or recurrence relations
                        - Specify base cases and memoization if needed
                        - Outline code structure""",
                        context=classification
                    )
                )
            
            strategies = await asyncio.gather(*strategy_promises)
            
            # Decompose problem for deeper understanding
            decomposition = await self.decompose(
                instruction="""Break down the problem into atomic subproblems:
                - Identify input preprocessing steps
                - Define core computation steps
                - Specify output formatting requirements
                - List all edge cases as separate subproblems
                - Establish dependencies between steps""",
                context=classification
            )
            
            # Synthesize best approach from strategies
            solution_draft = await self.ensemble(
                instruction=f"""Synthesize the optimal solution from these strategies and decomposition:
                Strategies: {strategies}
                Decomposition: {decomposition}
                
                Requirements:
                - Choose or merge the most robust, efficient approach
                - Incorporate all edge case handling from decomposition
                - Ensure type consistency and signature compliance
                - Output only the Python function code, no explanations""",
                contexts_list=strategies + [str(decomposition)]
            )

        # STEP 3: SELF-VALIDATION & EDGE CASE TESTING
        test_cases = await self.generate(
            instruction=f"""Generate 5 comprehensive test cases including edge cases:
            Based on problem classification: {classification}
            - Include normal cases
            - Include empty input case
            - Include single element case
            - Include boundary value cases
            - Include type variation cases if applicable
            Format as Python assert statements.""",
            context=solution_draft
        )
        
        # Validate solution against generated tests
        validation = await self.programmer(
            instruction=f"""Execute this code against these test cases:
            Code: {solution_draft}
            Test Cases: {test_cases}
            
            Return:
            - 'PASS' if all tests pass
            - 'FAIL: [reason]' if any test fails
            - Do not modify the code""",
            context=f"{solution_draft}\n\n{test_cases}",
            max_retries=1
        )

        # STEP 4: ITERATIVE REFINEMENT IF NEEDED
        current_solution = solution_draft
        for attempt in range(3):
            if "PASS" in validation:
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix this validation failure:
                Failure: {validation}
                Original Classification: {classification}
                Previous Solution: {current_solution}
                
                Requirements:
                - Fix the specific failure mentioned
                - Preserve correct behavior for other cases
                - Maintain clean, efficient code
                - Output only the revised Python function""",
                context=current_solution
            )
            
            # Re-validate
            validation = await self.programmer(
                instruction=f"""Re-test revised code:
                Code: {current_solution}
                Test Cases: {test_cases}
                Return 'PASS' or 'FAIL: [reason]'""",
                context=f"{current_solution}\n\n{test_cases}",
                max_retries=1
            )

        # STEP 5: PRECISION FORMATTING (CRITICAL)
        final_code = await self.revise(
            instruction="""Extract ONLY the Python function implementation with exact signature:
            - Remove any markdown, explanations, or extra text
            - Ensure function name matches problem exactly
            - Include necessary imports at top
            - Preserve all type handling and edge case logic
            - Return ONLY the raw code block, nothing else""",
            context=current_solution
        )

        # STEP 6: SANITY CHECK & FINAL OUTPUT
        # Ensure output is clean Python code
        code_lines = final_code.split('\n')
        cleaned_lines = []
        in_code_block = False
        
        for line in code_lines:
            if line.strip().startswith('