# Workflow ID: limr_147_0
# Benchmark: limr
# Data Indices: [323, 310]

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

        # Step 1: Initial problem analysis and classification
        initial_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            - The primary mathematical domain (algebra, geometry, number theory, combinatorics, etc.)
            - Key mathematical objects involved (functions, sequences, geometric figures, etc.)
            - Required solution techniques (proof, computation, optimization, etc.)
            - Any non-obvious transformations or insights needed
            - Potential pitfalls or common mistakes
            - Estimated complexity level (1-5, 5 being most complex)
            Format your response as a structured analysis with clear section headings.""",
            context=""
        )

        # Step 2: Generate multiple parallel solution strategies
        strategy_instructions = [
            """Develop a solution strategy focusing on algebraic manipulation and symbolic computation. 
            Look for substitutions, factorizations, or identities that can simplify the problem. 
            Show step-by-step reasoning and justify each transformation mathematically.""",
            
            """Develop a solution strategy focusing on numerical computation and algorithmic approaches.
            Consider whether the problem can be solved by writing a program or performing systematic calculations.
            Specify any required formulas, algorithms, or computational steps.""",
            
            """Develop a solution strategy focusing on geometric or visual reasoning.
            Even if the problem appears algebraic, consider whether a geometric interpretation exists.
            Use diagrams, coordinate systems, or spatial reasoning where applicable."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=initial_analysis) for instr in strategy_instructions]
        )

        # Step 3: Conditional decomposition based on complexity
        complexity_match = re.search(r'complexity level.*?([1-5])', initial_analysis.lower())
        complexity_level = int(complexity_match.group(1)) if complexity_match else 3

        if complexity_level >= 4:
            decomposition = await self.decompose(
                instruction="""Break this problem into the smallest possible subproblems that can be solved independently.
                Each subproblem should have clear inputs and outputs, and dependencies should be explicitly stated.
                Focus on creating a logical sequence that builds toward the final solution.""",
                context=initial_analysis
            )
            # Process decomposition - for now, we'll just use it as additional context
            decomposition_summary = await self.summarize(
                instruction="Summarize the decomposition into a clear roadmap for solving the problem.",
                context=str(decomposition)
            )
            strategies = [await self.generate(
                instruction=f"""Revise this strategy to incorporate the decomposition roadmap:
                {decomposition_summary}
                Ensure each step of the decomposition is addressed in your solution approach.""",
                context=strat
            ) for strat in strategies]

        # Step 4: Execute and validate each strategy
        async def execute_and_validate(strategy):
            for attempt in range(3):  # Max 3 attempts per strategy
                try:
                    # Execute the strategy
                    solution_attempt = await self.generate(
                        instruction="""Implement the solution strategy step by step.
                        Show all work, including intermediate calculations and reasoning.
                        Box your final answer at the end using \\boxed{{}} notation.
                        If you encounter an obstacle, explain what it is and how you might overcome it.""",
                        context=strategy
                    )
                    
                    # Validate the solution
                    validation = await self.generate(
                        instruction="""Critically evaluate this solution:
                        - Are all steps mathematically sound?
                        - Are there any calculation errors?
                        - Does the final answer make sense in context?
                        - Are there alternative approaches that might be better?
                        If you find any issues, describe them specifically and suggest corrections.
                        If the solution is correct, state "VALID" and explain why.""",
                        context=solution_attempt
                    )
                    
                    if "VALID" in validation.upper() and "error" not in validation.lower() and "issue" not in validation.lower():
                        return solution_attempt
                    
                    # If not valid, revise and try again
                    strategy = await self.revise(
                        instruction=f"""Revise the strategy based on this validation feedback:
                        {validation}
                        Address all identified issues and strengthen any weak points in the reasoning.""",
                        context=strategy
                    )
                except Exception as e:
                    continue  # Try next attempt if something goes wrong
            return solution_attempt  # Return last attempt even if not fully validated

        solutions = await asyncio.gather(*[execute_and_validate(strat) for strat in strategies])

        # Step 5: Ensemble synthesis - select or merge the best solutions
        final_solution = await self.ensemble(
            instruction="""You are given multiple solution attempts for the same mathematical problem.
            Evaluate each solution for:
            - Mathematical correctness
            - Clarity of reasoning
            - Completeness of steps
            - Elegance and efficiency
            Select the single best solution, or synthesize a new solution that combines the strongest elements of multiple attempts.
            Your final output should be a polished, complete solution with the answer boxed at the end.""",
            contexts_list=solutions
        )

        # Step 6: Final verification and formatting
        formatted_answer = await self.generate(
            instruction="""Extract the final numerical answer from the solution and format it as a 3-digit integer (000-999).
            - If the answer is not an integer, indicate ERROR
            - If the answer is outside 000-999, indicate ERROR
            - If multiple answers are present, select the most reasonable one
            - Zero-pad the answer to exactly 3 digits (e.g., 42 becomes 042)
            Output ONLY the 3-digit number or ERROR, nothing else.""",
            context=final_solution
        )

        # Clean up the answer format
        answer_match = re.search(r'\b(\d{1,3})\b', formatted_answer)
        if answer_match:
            answer = answer_match.group(1).zfill(3)
            if int(answer) <= 999:
                return answer
        
        # Fallback: try to extract any number from the final solution
        fallback_match = re.search(r'\\boxed\{(\d+)\}', final_solution)
        if fallback_match:
            answer = fallback_match.group(1).zfill(3)
            if int(answer) <= 999:
                return answer
        
        return "000"  # Default fallback