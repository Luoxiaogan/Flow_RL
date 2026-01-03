# Workflow ID: mbppplus_3_0
# Benchmark: mbppplus
# Data Indices: [200, 26]

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

        # Step 1: Classify problem type and estimate complexity
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:
            1. Categorize by primary domain: [list/tuple operations, string manipulation, mathematical computation, data structure algorithms, logic problems]
            2. Identify required output type: [function returning int, list, tuple, bool, etc.]
            3. Estimate complexity level: [simple, medium, complex] based on:
               - Number of edge cases implied
               - Algorithmic depth required
               - Recursion or advanced data structures needed
            4. List explicit and implicit constraints from the problem description.
            5. Suggest 2-3 potential solution strategies.
            Format your response as a structured JSON-like summary.""",
            context=""
        )

        # Step 2: Extract key requirements (return type, parameters, edge cases)
        requirements = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Extract precise implementation requirements:
            - Exact function signature (name, parameters)
            - Required return type and format
            - Critical edge cases to handle (empty inputs, single elements, duplicates, boundaries)
            - Any performance or efficiency constraints
            Present as bullet points with clear, actionable items.""",
            context=classification
        )

        # Step 3: Adaptive strategy - choose depth based on complexity
        complexity_check = await self.generate(
            instruction=f"""Based on this classification:
            {classification}
            
            Should we use:
            A) Simple direct solution (for trivial problems)
            B) Multi-strategy parallel generation (for medium/complex problems)
            Respond ONLY with 'A' or 'B'.""",
            context=classification
        )

        if 'B' in complexity_check:
            # Step 4: Generate multiple solution strategies in parallel
            strategy_instructions = [
                """Implement using a mathematical/set theory approach. Focus on elegance and minimal operations. Consider using built-in Python functions like set(), len(), etc.""",
                """Implement using iterative/loop-based logic. Be explicit about edge case handling. Prioritize readability and step-by-step clarity.""",
                """Implement using recursion or divide-and-conquer if applicable. Show clear base cases and recursive structure."""
            ]
            
            solution_candidates = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""{req}
                    
                    {strategy}
                    
                    IMPORTANT: 
                    - Match exact function signature from requirements
                    - Handle all edge cases mentioned in requirements
                    - Return correct data type
                    - Include necessary imports
                    - Code must be complete and runnable""",
                    context=requirements
                ) for strategy in strategy_instructions]
            )
            
            # Step 5: Ensemble - select best solution
            selected_solution = await self.ensemble(
                instruction="""Evaluate these candidate solutions:
                - Correctness: Does it handle all edge cases?
                - Efficiency: Is it computationally reasonable?
                - Clarity: Is the logic easy to follow?
                - Robustness: Does it gracefully handle unexpected inputs?
                Select the single best solution or synthesize a hybrid if one combines strengths.
                Return ONLY the code block, nothing else.""",
                contexts_list=solution_candidates
            )
        else:
            # Simple direct solution
            selected_solution = await self.programmer(
                instruction=f"""Implement the solution directly:
                {requirements}
                
                IMPORTANT:
                - Match exact function signature
                - Handle all edge cases
                - Return correct data type
                - Include necessary imports
                - Code must be complete and runnable""",
                context=requirements
            )

        # Step 6: Generate edge cases for validation
        edge_cases = await self.generate(
            instruction=f"""Based on the problem and requirements:
            {requirements}
            
            Generate 5-7 comprehensive test cases including:
            - Typical cases
            - Boundary conditions
            - Empty/edge inputs
            - Duplicate values (if applicable)
            - Type edge cases
            Format as Python assert statements.""",
            context=requirements
        )

        # Step 7: Revise solution with edge cases
        hardened_solution = await self.revise(
            instruction=f"""Improve this solution:
            {selected_solution}
            
            Using these edge cases:
            {edge_cases}
            
            Ensure:
            - All edge cases are handled
            - No type mismatches
            - Efficient and clean code
            - Proper imports included
            - Function signature exactly matches requirements
            Return ONLY the complete, corrected code.""",
            context=selected_solution
        )

        # Step 8: Confidence check - self-assessment
        confidence = await self.generate(
            instruction=f"""Rate this solution's robustness on a scale of 1-10:
            {hardened_solution}
            
            Consider:
            - Edge case coverage
            - Code clarity
            - Efficiency
            - Type safety
            - Adherence to requirements
            If score < 8, suggest specific improvements.
            Otherwise, respond 'CONFIDENT'.""",
            context=hardened_solution
        )

        # Step 9: Final revision if low confidence
        if 'CONFIDENT' not in confidence:
            final_solution = await self.revise(
                instruction=f"""Address these weaknesses:
                {confidence}
                
                Improve the solution:
                {hardened_solution}
                
                Return ONLY the complete, final code.""",
                context=hardened_solution
            )
        else:
            final_solution = hardened_solution

        # Step 10: Extract and return clean code block
        code_block_match = re.search(r'