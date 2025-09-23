# Workflow ID: mbppplus_136_0
# Benchmark: mbppplus
# Data Indices: [160, 32]

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

        # Phase 1: Parallel problem analysis - classification and constraint extraction
        classification_task = self.generate(
            instruction="""Analyze the problem to determine its fundamental type and required approach. Consider:
            - Is this a mathematical formula application, combinatorial iteration, string manipulation, or logical validation problem?
            - What data structures are involved (lists, tuples, sets, dictionaries)?
            - What is the expected computational complexity (O(1), O(n), O(n²), etc.)?
            - Are there obvious algorithmic patterns (bit manipulation, dynamic programming, greedy, etc.)?
            - What is the primary challenge: correctness, efficiency, edge cases, or type handling?
            Provide a structured classification with clear reasoning.""",
            context=""
        )
        
        constraint_task = self.generate(
            instruction="""Extract all explicit and implicit constraints, edge cases, and boundary conditions:
            - What input values would be considered invalid or require special handling?
            - Are there physical or mathematical limits (like angles > 360° or negative indices)?
            - What should happen with empty inputs, single elements, or extreme values?
            - Are there type conversion requirements or return type specifications?
            - What assumptions are being made that aren't explicitly stated?
            Organize findings as a bullet-point list with clear categories.""",
            context=""
        )

        # Execute both analyses in parallel
        classification, constraints = await asyncio.gather(classification_task, constraint_task)

        # Phase 2: Synthesize comprehensive solution plan
        solution_plan = await self.ensemble(
            instruction="""Synthesize the problem classification and constraint analysis into a unified solution strategy:
            1. Specify the exact computational approach (formula, nested loops, recursion, etc.)
            2. Detail required data transformations and type handling
            3. Outline edge case handling strategy with specific conditions
            4. Define expected return types and formats
            5. Identify potential failure points and validation checkpoints
            6. Suggest efficiency considerations and possible optimizations
            Present as a numbered, actionable plan that a programmer could follow step by step.""",
            contexts_list=[classification, constraints]
        )

        # Phase 3: Generate initial code solution
        initial_code = await self.programmer(
            instruction=f"""Implement the solution according to this plan:
            {solution_plan}
            
            Additional requirements:
            - Handle all edge cases identified in the constraints analysis
            - Ensure return types match exactly what's expected (int, float, list, tuple, None, etc.)
            - Include defensive programming for invalid inputs
            - Use clear, descriptive variable names
            - Avoid unnecessary complexity - prioritize correctness over cleverness
            - If the problem involves mathematical constants, use precise values (like 22/7 for pi if specified)
            - For combinatorial problems, ensure you're processing all required pairs/elements
            Return only the function implementation as specified in the problem signature.""",
            context=solution_plan
        )

        # Phase 4: Iterative refinement with validation feedback
        current_code = initial_code
        max_retries = 3
        
        for attempt in range(max_retries):
            # Validate and revise code
            revised_code = await self.revise(
                instruction=f"""Critically evaluate this code implementation:
                {current_code}
                
                Check against:
                1. Problem classification: Does the approach match the identified problem type?
                2. Constraint handling: Are all edge cases and boundary conditions properly addressed?
                3. Return type: Does it match exactly what's expected?
                4. Mathematical accuracy: Are formulas and calculations correct?
                5. Efficiency: Is the solution unnecessarily complex or inefficient?
                6. Code quality: Is it readable, well-structured, and defensively programmed?
                
                If any issues are found, revise the code to fix them. If no issues are found, return the code unchanged.
                Return only the function implementation.""",
                context=current_code
            )
            
            # If code hasn't changed, we're done
            if revised_code.strip() == current_code.strip():
                break
                
            current_code = revised_code

        # Phase 5: Final optimization and efficiency check (parallel)
        optimization_task = self.generate(
            instruction=f"""Analyze the current solution for potential optimizations:
            {current_code}
            
            Consider:
            - Can any mathematical formulas be simplified or precomputed?
            - Are there algorithmic improvements (O(n²) → O(n), etc.)?
            - Can space complexity be reduced?
            - Are there redundant calculations that can be eliminated?
            - Would bit manipulation, memoization, or other techniques help?
            If no meaningful optimizations exist, state "No optimizations needed."
            Otherwise, provide the optimized code with explanation.""",
            context=current_code
        )
        
        type_check_task = self.generate(
            instruction=f"""Verify type handling and edge case coverage:
            {current_code}
            
            Specifically check:
            - Does the code handle all edge cases identified earlier?
            - Are return types consistent with problem requirements?
            - Are there any type conversion issues or assumptions?
            - Does it gracefully handle invalid inputs as specified?
            If any issues found, provide corrected code. Otherwise, return "Type handling verified."""",
            context=current_code
        )

        # Execute optimization and type checking in parallel
        optimization_result, type_check_result = await asyncio.gather(optimization_task, type_check_task)

        # Phase 6: Final ensemble to select best version
        final_code = await self.ensemble(
            instruction=f"""Select the best final implementation from these options:
            Option 1 (Current): {current_code}
            Option 2 (Optimized): {optimization_result}
            Option 3 (Type-corrected): {type_check_result}
            
            Selection criteria:
            1. Correctness: Must handle all edge cases and constraints
            2. Type fidelity: Return types must match exactly
            3. Efficiency: Prefer more efficient solutions when correctness is equal
            4. Readability: Prefer clearer, more maintainable code
            5. Robustness: Better error handling and defensive programming
            
            Return only the selected function implementation. If multiple are equally good, prefer the current version.""",
            contexts_list=[current_code, optimization_result, type_check_result]
        )

        return final_code