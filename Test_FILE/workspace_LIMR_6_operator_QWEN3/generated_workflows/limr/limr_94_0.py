# Workflow ID: limr_94_0
# Benchmark: limr
# Data Indices: [244, 64]

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

        # PHASE 1: META-ANALYSIS & STRATEGY GENERATION
        problem_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this mathematical problem:
            1. Classify the primary domain (algebra, geometry, number theory, combinatorics, calculus, etc.)
            2. Identify secondary domains or cross-domain elements
            3. List all mathematical objects involved (functions, shapes, sequences, etc.)
            4. Extract explicit and implicit constraints
            5. Determine the nature of the expected answer (integer, expression, proof, etc.)
            6. Propose 3 distinct high-level solution strategies with brief rationale for each
            7. Flag any potential pitfalls or common mistakes for this problem type
            8. Estimate complexity level (low/medium/high) and required steps
            Format your response with clear section headers for each point above.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        strategy_prompts = [
            """Develop Strategy 1 from the analysis into a detailed step-by-step solution plan.
            - Break down into logical phases
            - Specify required mathematical tools for each phase
            - Identify potential failure points and fallbacks
            - Include verification checkpoints
            Reference the original problem and analysis as needed.""",
            
            """Develop Strategy 2 from the analysis into a detailed step-by-step solution plan.
            - Break down into logical phases
            - Specify required mathematical tools for each phase
            - Identify potential failure points and fallbacks
            - Include verification checkpoints
            Reference the original problem and analysis as needed.""",
            
            """Develop Strategy 3 from the analysis into a detailed step-by-step solution plan.
            - Break down into logical phases
            - Specify required mathematical tools for each phase
            - Identify potential failure points and fallbacks
            - Include verification checkpoints
            Reference the original problem and analysis as needed."""
        ]

        strategy_plans = await asyncio.gather(
            *[self.generate(instruction=prompt, context=problem_analysis) for prompt in strategy_prompts]
        )

        # PHASE 3: HIERARCHICAL DECOMPOSITION & DEPENDENCY RESOLUTION
        async def execute_strategy(strategy_plan):
            try:
                # Decompose the strategy into subproblems
                subproblems = await self.decompose(
                    instruction="""Break this solution strategy into atomic subproblems:
                    - Each subproblem should be solvable independently or with specified dependencies
                    - Include mathematical prerequisites for each
                    - Estimate difficulty and required tools
                    - Output in the exact format: list of dicts with 'id', 'description', 'dependencies'""",
                    context=strategy_plan
                )
                
                # Execute subproblems respecting dependencies
                results = {}
                # Simple topological sort - assuming no circular dependencies
                subproblem_dict = {sp['id']: sp for sp in subproblems}
                solved_ids = set()
                
                for _ in range(len(subproblems)):  # Safety limit
                    progress = False
                    for sp in subproblems:
                        sp_id = sp['id']
                        if sp_id in solved_ids:
                            continue
                        deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                        if all(dep.strip() in solved_ids for dep in deps if dep.strip()):
                            # All dependencies satisfied, solve this subproblem
                            context_for_subproblem = f"Strategy: {strategy_plan}\n\nSubproblem: {sp['description']}\n\nPrevious results: {results}"
                            
                            # Decide whether to use generate or programmer based on subproblem type
                            if any(keyword in sp['description'].lower() for keyword in ['calculate', 'compute', 'numerical', 'value', 'solve equation']):
                                sub_result = await self.programmer(
                                    instruction=f"""Solve this mathematical subproblem precisely:
                                    {sp['description']}
                                    Use exact arithmetic. Show all steps. Verify result.
                                    If symbolic solution is impossible, use numerical methods with high precision.
                                    Return only the final answer in boxed format.""",
                                    context=context_for_subproblem,
                                    max_retries=3
                                )
                            else:
                                sub_result = await self.generate(
                                    instruction=f"""Solve this mathematical subproblem with rigorous reasoning:
                                    {sp['description']}
                                    Show all logical steps. Justify each assertion. Verify result.
                                    Return only the final answer in boxed format.""",
                                    context=context_for_subproblem
                                )
                            
                            # Validate and revise if necessary
                            validation = await self.generate(
                                instruction="""Critically examine this subproblem solution:
                                - Check for mathematical errors
                                - Verify it satisfies all constraints
                                - Ensure it's consistent with previous results
                                - Flag any approximations or assumptions
                                If errors found, suggest corrections.""",
                                context=f"Subproblem: {sp['description']}\n\nSolution: {sub_result}"
                            )
                            
                            if "error" in validation.lower() or "incorrect" in validation.lower() or "flaw" in validation.lower():
                                sub_result = await self.revise(
                                    instruction=f"""Revise the solution based on this critique:
                                    {validation}
                                    Maintain mathematical rigor. Show corrected steps.""",
                                    context=sub_result
                                )
                            
                            results[sp_id] = sub_result
                            solved_ids.add(sp_id)
                            progress = True
                    
                    if not progress:
                        break  # Deadlock or circular dependency
                
                # Synthesize final answer from subproblem results
                synthesis = await self.generate(
                    instruction="""Synthesize all subproblem results into a final answer:
                    - Combine partial results logically
                    - Verify consistency across all components
                    - Ensure final answer matches problem requirements
                    - Format as a single integer between 000 and 999
                    - If answer is not in this range, apply appropriate transformation (mod 1000, etc.)""",
                    context=f"Strategy Plan: {strategy_plan}\n\nSubproblem Results: {results}"
                )
                
                return synthesis
                
            except Exception as e:
                return f"STRATEGY_FAILED: {str(e)}"

        # Execute all strategies in parallel
        strategy_results = await asyncio.gather(
            *[execute_strategy(plan) for plan in strategy_plans]
        )

        # PHASE 4: ENSEMBLE SYNTHESIS & CONSENSUS BUILDING
        final_answer = await self.ensemble(
            instruction="""Synthesize the results from multiple solution strategies:
            1. Compare all strategy results for consistency
            2. Identify the most reliable answer based on:
               - Mathematical rigor
               - Consistency with problem constraints
               - Verification steps included
               - Absence of flagged errors
            3. If results conflict, perform root cause analysis and select the most defensible answer
            4. Ensure final answer is an integer between 000 and 999
            5. If no strategy succeeded, generate a fallback solution using the most promising approach
            6. Present ONLY the final integer answer in the format: \\boxed{XXX}""",
            contexts_list=[str(r) for r in strategy_results]
        )

        # PHASE 5: FINAL VERIFICATION & FORMATTING
        verified_answer = await self.revise(
            instruction="""Final verification and formatting:
            1. Extract the integer answer from the provided solution
            2. Ensure it is between 000 and 999 (inclusive)
            3. If it's a mathematical expression, evaluate it to an integer
            4. If it's outside range, apply modulo 1000 or other appropriate transformation as implied by problem context
            5. Format as exactly three digits with leading zeros if necessary
            6. Return ONLY the three-digit number, no other text or explanation""",
            context=final_answer
        )

        # Extract just the three-digit number using regex as final safety
        match = re.search(r'\b(\d{3})\b', verified_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and format to 3 digits
            numbers = re.findall(r'\d+', verified_answer)
            if numbers:
                num = int(numbers[0]) % 1000
                return f"{num:03d}"
            else:
                return "000"  # Ultimate fallback