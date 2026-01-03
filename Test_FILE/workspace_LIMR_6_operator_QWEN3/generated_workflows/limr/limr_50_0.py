# Workflow ID: limr_50_0
# Benchmark: limr
# Data Indices: [142, 331]

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

        # Step 1: Initial problem analysis and constraint extraction
        initial_analysis = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Identify the mathematical domain (geometry, algebra, combinatorics, number theory, etc.)
            2. Extract all given quantities, constraints, and target variables
            3. Note any symmetries, invariants, or special properties (e.g., regular polygons, symmetric sums)
            4. Identify potential solution strategies (coordinate geometry, Newton's identities, angle chasing, etc.)
            5. Flag any potential traps or non-obvious insights required
            Format as a structured markdown report with clear sections.""",
            context=""
        )

        # Step 2: Hierarchical decomposition into subproblems
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal solvable subproblems:
            - Use the analysis: {initial_analysis}
            - Each subproblem should be independently solvable or have clear dependencies
            - Prioritize subproblems that unlock others
            - Include both computational and conceptual subproblems
            - For geometry: consider coordinate, vector, and synthetic approaches
            - For algebra: consider symmetric sums, recurrence, substitution
            Return as list of subproblems with dependencies.""",
            context=initial_analysis
        )

        # Step 3: Parallel solution strategy generation for each subproblem
        strategy_tasks = []
        for i, subproblem in enumerate(decomposition):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            strategy_task = self.generate(
                instruction=f"""Generate 3 distinct solution strategies for subproblem {sp_id}:
                Description: {sp_desc}
                
                Strategies should include:
                - One computational/algorithmic approach (suitable for Programmer)
                - One analytical/reasoning approach (pure mathematical derivation)
                - One geometric/visual or combinatorial approach (if applicable)
                
                For each strategy:
                1. Outline the key steps
                2. List required formulas or theorems
                3. Estimate complexity and potential pitfalls
                4. Rate confidence (1-10) based on problem constraints
                
                Format as numbered list with clear strategy headers.""",
                context=initial_analysis
            )
            strategy_tasks.append(strategy_task)
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Step 4: Execute top strategy for each subproblem (with fallback)
        subproblem_solutions = {}
        for i, subproblem in enumerate(decomposition):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            strategies = strategy_results[i]
            
            # Select most confident strategy via ensemble
            strategy_selection = await self.ensemble(
                instruction=f"""Select the single best strategy for subproblem {sp_id}:
                Criteria:
                1. Highest confidence score
                2. Minimal computational complexity
                3. Best alignment with given constraints
                4. Avoids known pitfalls mentioned in analysis
                
                Justify your selection and extract the exact steps to execute.""",
                contexts_list=[strategies]
            )
            
            # Attempt computational solution first
            solution = None
            for attempt in range(3):  # Max 3 attempts
                try:
                    if "PROGRAM" in strategy_selection.upper() or "COMPUT" in strategy_selection.upper():
                        solution = await self.programmer(
                            instruction=f"""Execute this strategy for subproblem {sp_id}:
                            Strategy: {strategy_selection}
                            Subproblem: {sp_desc}
                            
                            Requirements:
                            - Write clean, well-commented Python code
                            - Include all necessary mathematical imports
                            - Verify intermediate results
                            - Return final answer as integer or simplified fraction
                            - If symbolic, convert to numeric value if possible""",
                            context=strategy_selection,
                            max_retries=1
                        )
                    else:
                        # Analytical approach
                        solution = await self.generate(
                            instruction=f"""Execute this analytical strategy for subproblem {sp_id}:
                            Strategy: {strategy_selection}
                            Subproblem: {sp_desc}
                            
                            Requirements:
                            - Show all mathematical steps
                            - Justify each transformation
                            - Box final answer
                            - Verify against original constraints""",
                            context=strategy_selection
                        )
                    
                    # Validate solution
                    validation = await self.generate(
                        instruction=f"""Validate this solution for subproblem {sp_id}:
                        Solution: {solution}
                        Original subproblem: {sp_desc}
                        
                        Check:
                        1. Does it satisfy all constraints?
                        2. Is the answer format correct (integer or simplified)?
                        3. Are there any calculation errors?
                        4. Does it align with initial problem analysis?
                        
                        If valid, respond "VALID: [answer]". If invalid, explain why.""",
                        context=solution
                    )
                    
                    if "VALID" in validation.upper():
                        # Extract answer
                        match = re.search(r'VALID:\s*([0-9\-\.\/]+)', validation)
                        if match:
                            solution = match.group(1)
                        subproblem_solutions[sp_id] = solution
                        break
                    else:
                        # Revise strategy
                        strategy_selection = await self.revise(
                            instruction=f"""Revise strategy based on validation failure:
                            Validation feedback: {validation}
                            Original strategy: {strategy_selection}
                            
                            Modify approach to fix identified issues.
                            Consider alternative methods if necessary.""",
                            context=strategy_selection
                        )
                except Exception as e:
                    # Fallback: try analytical if computational failed
                    strategy_selection = await self.revise(
                        instruction=f"""Switch to analytical approach due to computational failure:
                        Error: {str(e)}
                        Original strategy: {strategy_selection}
                        
                        Reformulate as pure mathematical derivation.""",
                        context=strategy_selection
                    )
            
            if sp_id not in subproblem_solutions:
                # Final fallback: take first strategy result
                subproblem_solutions[sp_id] = f"FALLBACK_{sp_id}"

        # Step 5: Synthesize subproblem solutions into final answer
        synthesis_context = "\n".join([f"Subproblem {sp_id}: {solution}" for sp_id, solution in subproblem_solutions.items()])
        
        final_synthesis = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into final answer:
            Subproblem solutions:
            {synthesis_context}
            
            Steps:
            1. Combine results according to problem dependencies
            2. Resolve any inconsistencies between subproblems
            3. Compute final answer (must be integer 000-999)
            4. Verify against original problem statement
            5. Box final answer as \boxed{{}}""",
            context=synthesis_context
        )

        # Step 6: Final validation and formatting
        final_answer = await self.revise(
            instruction="""Ensure final answer meets all requirements:
            1. Must be an integer between 000 and 999
            2. Must be boxed as \boxed{number}
            3. Must be derived from valid mathematical reasoning
            4. If answer is fractional or decimal, convert to integer (round if appropriate, but prefer exact)
            5. If multiple answers possible, select most reasonable based on context
            
            If answer doesn't meet criteria, revise solution path and recalculate.""",
            context=final_synthesis
        )

        # Extract final boxed answer
        box_match = re.search(r'\\boxed\{(\d{1,3})\}', final_answer)
        if box_match:
            return f"\\boxed{{{int(box_match.group(1)):03d}}}"
        else:
            # Fallback: return as is but ensure 3-digit format if numeric
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000
                return f"\\boxed{{{num:03d}}}"
            else:
                return "\\boxed{000}"  # Ultimate fallback