# Workflow ID: mbppplus_101_0
# Benchmark: mbppplus
# Data Indices: [10, 340, 139]

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

        # STEP 1: Extract implicit constraints and edge cases
        constraint_analysis = await self.generate(
            instruction="""Thoroughly analyze the problem to extract ALL implicit constraints and edge cases. Consider:
            - Function signature: parameter types, return type, naming conventions
            - Data structure expectations: lists, tuples, sets, dictionaries
            - Boundary conditions: empty inputs, single elements, maximum/minimum values
            - Type safety: what if input contains mixed or unexpected types?
            - Index safety: if accessing by index, what if index is out of bounds?
            - Order preservation: does the problem care about order?
            - Duplicate handling: should duplicates be preserved, removed, or counted?
            - Performance: are there efficiency constraints?
            - Error handling: should the function raise errors or return defaults?
            Format as a numbered list with clear, concise bullet points.""",
            context=""
        )

        # STEP 2: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Propose a complete solution strategy for this problem. 
                Strategy 1: Direct iterative approach with explicit loops and conditionals.
                - Use traditional for/while loops
                - Include explicit edge case checks
                - Prioritize readability and debuggability
                Constraints to consider:
                {constraint_analysis}
                Output ONLY the Python function implementation with necessary imports.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a complete solution strategy for this problem.
                Strategy 2: Functional/comprehension-based approach.
                - Use list/dict comprehensions, map/filter, or generator expressions
                - Leverage built-in functions (max, min, sum, etc.)
                - Prioritize conciseness and functional purity
                Constraints to consider:
                {constraint_analysis}
                Output ONLY the Python function implementation with necessary imports.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a complete solution strategy for this problem.
                Strategy 3: Recursive or divide-and-conquer approach.
                - Break problem into smaller subproblems
                - Use recursion or hierarchical processing
                - Consider memoization if applicable
                Constraints to consider:
                {constraint_analysis}
                Output ONLY the Python function implementation with necessary imports.""",
                context=""
            )
        ]
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # STEP 3: Validate each strategy against edge cases
        validation_tasks = []
        for i, candidate in enumerate(strategy_candidates):
            validation = await self.generate(
                instruction=f"""Critically validate this solution against the constraints and edge cases.
                Solution to validate:
                {candidate}
                
                Constraints:
                {constraint_analysis}
                
                Perform mental simulation of edge cases:
                - Empty inputs
                - Single element inputs
                - Boundary values
                - Type mismatches
                - Index out of bounds
                - Duplicate values
                - Order sensitivity
                
                Identify any flaws, crashes, or inconsistencies.
                Rate confidence as HIGH/MEDIUM/LOW.
                If LOW or MEDIUM, suggest specific fixes.
                Format: [CONFIDENCE: X] followed by bullet-pointed analysis.""",
                context=candidate
            )
            validation_tasks.append(validation)
        
        validations = await asyncio.gather(*validation_tasks)

        # STEP 4: Ensemble select best strategy or trigger fallback
        confidence_scores = []
        for validation in validations:
            if "HIGH" in validation.split('\n')[0].upper():
                confidence_scores.append(3)
            elif "MEDIUM" in validation.split('\n')[0].upper():
                confidence_scores.append(2)
            else:
                confidence_scores.append(1)

        # If all confidence is low, trigger deeper analysis
        if max(confidence_scores) < 3:
            fallback_analysis = await self.generate(
                instruction=f"""All initial strategies have low confidence. Perform deep re-analysis:
                - Re-examine problem statement for misunderstood requirements
                - Consult common pitfalls in this domain: type coercion, off-by-one errors, mutable defaults
                - Consider alternative interpretations of the task
                - Generate one new, radically different approach
                Constraints:
                {constraint_analysis}
                Output ONLY the Python function implementation with necessary imports.""",
                context="\n".join(validations)
            )
            final_solution = fallback_analysis
        else:
            # Select highest confidence solution
            best_index = confidence_scores.index(max(confidence_scores))
            selected_solution = strategy_candidates[best_index]
            
            # Final polish: ensure perfect format and type consistency
            final_solution = await self.revise(
                instruction="""Final polish: ensure output matches EXACT requirements:
                - Function name must match exactly
                - Parameter names must match exactly
                - Return type must be correct (list vs tuple vs dict vs set)
                - Include necessary imports at top
                - No wrapper functions or classes
                - Handle all edge cases identified in constraints
                - Code must be clean, efficient, and readable
                Output ONLY the final Python function implementation.""",
                context=selected_solution
            )

        return final_solution