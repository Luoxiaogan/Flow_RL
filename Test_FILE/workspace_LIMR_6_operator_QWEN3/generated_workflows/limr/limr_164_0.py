# Workflow ID: limr_164_0
# Benchmark: limr
# Data Indices: [338, 158]

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

        # PHASE 1: Problem Decomposition & Classification
        decomposition = await self.decompose(
            instruction="""Break down this mathematical problem into fundamental subproblems. For each:
            - Identify what mathematical domain it belongs to (algebra, number theory, combinatorics, geometry, optimization)
            - Specify whether it requires symbolic manipulation, computational evaluation, or conceptual insight
            - Note any symmetries, invariants, or constraints
            - Determine dependencies between subproblems
            - Flag if a subproblem might have multiple solution paths
            Return a structured list with clear, atomic subproblems.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Exploration
        strategy_tasks = []
        for i, subproblem in enumerate(decomposition):
            sub_desc = subproblem['description']
            strategy_task = self.generate(
                instruction=f"""For this subproblem: "{sub_desc}"
                Generate THREE distinct solution strategies. For each:
                - Name the mathematical principle or theorem applied (e.g., AM-GM, modular arithmetic, combinatorial identity)
                - Outline the step-by-step approach
                - Note potential pitfalls or assumptions
                - Estimate computational complexity (low/medium/high)
                Format each strategy clearly with headers.""",
                context=""
            )
            strategy_tasks.append(strategy_task)
        
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Strategy Refinement & Computational Routing
        refined_solutions = []
        for i, strategies in enumerate(raw_strategies):
            subproblem = decomposition[i]
            
            # Check if subproblem is computational
            if "compute" in subproblem['description'].lower() or "evaluate" in subproblem['description'].lower():
                # Route to programmer with specific instruction
                try:
                    computation = await self.programmer(
                        instruction=f"""Given this mathematical subproblem: {subproblem['description']}
                        Write Python code to compute the exact result. Use sympy if symbolic computation is needed.
                        Ensure all variables are properly initialized and constraints are enforced.
                        Output only the final numerical result.""",
                        context=strategies
                    )
                    refined_solutions.append(computation)
                except Exception:
                    # Fallback to generate if programmer fails
                    fallback = await self.generate(
                        instruction=f"""Since computational approach failed, solve this subproblem symbolically: {subproblem['description']}
                        Show all algebraic steps and justify each transformation.
                        Box the final result.""",
                        context=strategies
                    )
                    refined_solutions.append(fallback)
            else:
                # Refine the best strategy through revision
                refined = await self.revise(
                    instruction="""Improve this solution strategy:
                    - Fill in any missing mathematical justifications
                    - Correct any logical gaps or algebraic errors
                    - Add explicit references to theorems or identities used
                    - Ensure the solution path is complete and self-contained
                    - Highlight the final result clearly""",
                    context=strategies
                )
                refined_solutions.append(refined)

        # PHASE 4: Cross-Validation & Error Checking
        validation_tasks = []
        for solution in refined_solutions:
            validation = self.generate(
                instruction=f"""Critically validate this solution:
                - Check for algebraic or logical errors
                - Verify dimensional consistency (if applicable)
                - Confirm adherence to original constraints
                - Test boundary cases or special values
                - Assess whether the conclusion follows from the premises
                If errors are found, describe them specifically. Otherwise, state 'VALID'.""",
                context=solution
            )
            validation_tasks.append(validation)
        
        validations = await asyncio.gather(*validation_tasks)

        # PHASE 5: Iterative Refinement (if errors detected)
        final_solutions = []
        for i, (solution, validation) in enumerate(zip(refined_solutions, validations)):
            if "error" in validation.lower() or "invalid" in validation.lower():
                # Revise up to 2 times
                current = solution
                for attempt in range(2):
                    revised = await self.revise(
                        instruction=f"""Fix the errors identified in validation: {validation}
                        Rewrite the solution with corrections. Maintain mathematical rigor.
                        If the original approach is fundamentally flawed, switch to an alternative strategy from the initial three.""",
                        context=current
                    )
                    # Re-validate
                    revalidation = await self.generate(
                        instruction="Re-validate this revised solution for errors.",
                        context=revised
                    )
                    if "error" not in revalidation.lower() and "invalid" not in revalidation.lower():
                        current = revised
                        break
                    current = revised
                final_solutions.append(current)
            else:
                final_solutions.append(solution)

        # PHASE 6: Ensemble Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize the solutions to all subproblems into a complete, coherent answer to the original problem.
            - Ensure all subproblem results are correctly integrated
            - Resolve any inconsistencies between subproblem solutions
            - Present the final answer as a single integer between 000 and 999
            - Show the complete logical flow from problem statement to final answer
            - Box the final numerical answer in the format \\boxed{XXX}""",
            contexts_list=final_solutions
        )

        # PHASE 7: Answer Extraction & Formatting
        formatted_answer = await self.generate(
            instruction="""Extract the final numerical answer from the solution.
            - Ensure it is an integer between 000 and 999
            - If multiple answers are present, select the one that satisfies all constraints
            - Format as a 3-digit string with leading zeros if necessary (e.g., 5 becomes "005")
            - Output ONLY the 3-digit string, nothing else.""",
            context=final_answer
        )

        # Clean and return
        # Extract 3-digit number using regex as final safeguard
        match = re.search(r'\b\d{1,3}\b', formatted_answer)
        if match:
            num = int(match.group())
            if 0 <= num <= 999:
                return f"{num:03d}"
        
        # Fallback: return 000 if extraction fails (shouldn't happen with proper validation)
        return "000"