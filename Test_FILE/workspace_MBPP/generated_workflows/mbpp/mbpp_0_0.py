# Workflow ID: mbpp_0_0
# Benchmark: mbpp
# Data Indices: [0]

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
        # Stage 1: Parallel extraction of key components
        signature_task = self.generate(
            instruction="""Extract the exact function signature from the test cases:
            - Function name (MUST match assert statements exactly)
            - Number of parameters
            - Infer parameter types from usage (e.g., if 'Pair' is used, assume it has .first and .second)
            - Expected return type
            Format as: "def function_name(param1: type1, param2: type2) -> return_type"
            If type is unclear, use 'Any' but note the uncertainty.""",
            context=""
        )
        
        task_interpretation_task = self.generate(
            instruction="""Interpret the natural language task description:
            - Identify the core objective
            - List explicit requirements
            - Note any ambiguous terms that need clarification
            - Propose 2-3 possible interpretations if ambiguity exists
            Structure output with clear headings.""",
            context=""
        )
        
        test_analysis_task = self.generate(
            instruction="""Analyze test cases to uncover hidden constraints:
            - What patterns do inputs follow? (sorted? unsorted? duplicates?)
            - What edge cases are implied? (empty input? single element?)
            - What does the expected output suggest about the algorithm?
            - Are there any contradictions between task description and test cases?
            Output as structured analysis with bullet points.""",
            context=""
        )
        
        # Gather parallel results
        signature, task_interp, test_analysis = await asyncio.gather(
            signature_task, task_interpretation_task, test_analysis_task
        )
        
        # Stage 2: Synthesize unified problem spec
        problem_spec = await self.ensemble(
            instruction=f"""Synthesize a complete problem specification from these components:
            TASK INTERPRETATION:
            {task_interp}
            
            TEST CASE ANALYSIS:
            {test_analysis}
            
            FUNCTION SIGNATURE:
            {signature}
            
            Create a unified spec that:
            1. Resolves ambiguities using test cases as ground truth
            2. Documents all assumptions made
            3. Specifies exact algorithmic requirements
            4. Lists edge cases to handle
            5. Defines success criteria beyond just passing tests
            Format as markdown with clear sections.""",
            contexts_list=[signature, task_interp, test_analysis]
        )
        
        # Stage 3: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Strategy 1 (Greedy/Heuristic):
                Problem Spec: {problem_spec}
                
                Design a greedy or heuristic solution:
                - Prioritize simplicity and efficiency
                - Document assumptions
                - Include step-by-step logic
                - Note limitations or edge cases it might miss""",
                context=problem_spec
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 2 (Dynamic Programming/Exhaustive):
                Problem Spec: {problem_spec}
                
                Design a DP or exhaustive solution:
                - Prioritize correctness over efficiency
                - Handle all edge cases explicitly
                - Document state transitions or recursion
                - Note computational complexity""",
                context=problem_spec
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 3 (Library/Pythonic):
                Problem Spec: {problem_spec}
                
                Design a solution using Python standard library:
                - Use built-in functions, itertools, functools etc.
                - Prioritize readability and idiomatic Python
                - Document which libraries are needed
                - Note any limitations of this approach""",
                context=problem_spec
            )
        )
        
        # Stage 4: Select best strategy based on test cases
        selected_strategy = await self.ensemble(
            instruction=f"""Select the optimal solution strategy:
            Problem Spec: {problem_spec}
            Strategies: {strategies}
            
            Criteria:
            1. Must pass all test cases (simulate execution mentally)
            2. Prefer simplest solution that meets requirements
            3. Must handle all documented edge cases
            4. Should be efficient for given input sizes
            5. Should use standard library if appropriate
            
            Output the selected strategy and justification.""",
            contexts_list=strategies
        )
        
        # Stage 5: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code from selected strategy:
            Strategy: {selected_strategy}
            Problem Spec: {problem_spec}
            
            Requirements:
            - Function name MUST match test cases exactly
            - Include all necessary imports (even if none, include comment)
            - Use 4-space indentation
            - Handle all edge cases from problem spec
            - Add brief comments explaining key steps
            - No debug prints or extra output
            - Return correct type as per signature
            
            Output ONLY the code in a markdown python block.""",
            context=selected_strategy
        )
        
        # Stage 6: Iterative refinement with simulated validation
        current_code = initial_code
        for iteration in range(3):  # Max 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Simulate validation of this code against test cases:
                Code: {current_code}
                Test Cases: {test_analysis}
                Problem Spec: {problem_spec}
                
                For each test case:
                1. Walk through execution step by step
                2. Verify output matches expected
                3. Check for edge case handling
                4. Identify any bugs or mismatches
                
                If all pass, output "VALID". Otherwise, list specific fixes needed.""",
                context=current_code
            )
            
            if "VALID" in validation.upper() and "FIX" not in validation.upper():
                break  # Success!
            
            # Revise code based on validation feedback
            current_code = await self.revise(
                instruction=f"""Revise code based on validation feedback:
                Current Code: {current_code}
                Validation Feedback: {validation}
                Problem Spec: {problem_spec}
                
                Make minimal changes to fix identified issues.
                Preserve function signature and overall structure.
                Ensure all edge cases are handled.
                Maintain clean, readable code with 4-space indentation.
                
                Output ONLY the revised code in markdown python block.""",
                context=current_code
            )
        
        # Stage 7: Final polish and formatting
        final_code = await self.revise(
            instruction=f"""Final polish for production-ready code:
            Code: {current_code}
            Problem Spec: {problem_spec}
            
            Ensure:
            - Perfect 4-space indentation
            - All necessary imports at top (add 'from typing import Any' if needed)
            - Function name exactly matches test cases
            - No syntax errors or undefined variables
            - Clean, professional formatting
            - Comments only where necessary for clarity
            - Handles all edge cases from spec
            
            Output ONLY the final code in markdown python block.""",
            context=current_code
        )
        
        return final_code