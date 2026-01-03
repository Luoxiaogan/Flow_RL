# Workflow ID: limr_33_0
# Benchmark: limr
# Data Indices: [109, 135]

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

        # PHASE 1: Deep Structural Decomposition
        decomposition = await self.decompose(
            instruction="""Break this mathematical problem into atomic, logically dependent subproblems.
            For each subproblem:
            - State precisely what needs to be computed or proven
            - Identify required inputs and expected outputs
            - List mathematical tools or theorems likely needed
            - Specify dependencies on other subproblems
            Prioritize foundational subproblems (e.g., solving for variables) before derived ones (e.g., computing area).
            Include a 'validation' subproblem to check final answer against all constraints.""",
            context=""
        )

        # PHASE 2: Multi-Perspective Strategy Generation (Parallel)
        strategy_instructions = [
            """Adopt an ALGEBRAIC perspective. Based on the decomposition, outline a step-by-step solution strategy focusing on:
            - Variable isolation and equation setup
            - Polynomial manipulation or system solving
            - Domain constraints and validity checks
            - Symbolic simplification before numerical computation
            Reference specific algebraic theorems or identities that apply.""",
            
            """Adopt a GEOMETRIC/COORDINATE perspective. Outline a solution strategy focusing on:
            - Coordinate system placement and point assignment
            - Distance, angle, or area formulas applicable
            - Transformation or symmetry exploitation
            - Vector or trigonometric approaches if relevant
            Explicitly state geometric assumptions being made.""",
            
            """Adopt a COMPUTATIONAL/NUMERICAL perspective. Outline a strategy focusing on:
            - Direct computation via code
            - Iterative methods or brute-force search if analytical solution is complex
            - Precision handling and edge case enumeration
            - Validation through substitution or reverse calculation
            Specify what variables to loop over and what conditions to check."""
        ]

        # Generate initial strategies in parallel
        raw_strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=json.dumps(decomposition)) 
              for instr in strategy_instructions]
        )

        # Refine each strategy for completeness and rigor
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Enhance this strategy:
                - Fill any logical gaps or missing steps
                - Add specific formulas or computational procedures
                - Include validation steps at critical junctures
                - Ensure all constraints from decomposition are addressed
                - Format as numbered steps with clear dependencies""",
                context=strat
            ) for strat in raw_strategies]
        )

        # PHASE 3: Parallel Execution and Adversarial Validation
        execution_tasks = []
        validation_tasks = []

        for i, strategy in enumerate(refined_strategies):
            # Execute each strategy
            exec_task = self.generate(
                instruction=f"""Implement this solution strategy step by step.
                - Show all intermediate calculations or reasoning
                - If computation is needed, describe it precisely (code will be generated separately)
                - Box the final answer at the end
                - If multiple answers are possible, list all and justify selection""",
                context=strategy
            )
            execution_tasks.append(exec_task)

            # Generate adversarial validation for each
            val_task = self.generate(
                instruction=f"""Critique this solution strategy and its implementation:
                - Identify any unjustified assumptions
                - Check for arithmetic or logical errors
                - Verify all constraints are satisfied
                - Propose counterexamples or edge cases
                - Suggest improvements or alternative approaches""",
                context=strategy
            )
            validation_tasks.append(val_task)

        # Run executions and validations in parallel
        executions = await asyncio.gather(*execution_tasks)
        validations = await asyncio.gather(*validation_tasks)

        # Revise executions based on validations
        revised_executions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Incorporate validation feedback:
                - Correct any identified errors
                - Strengthen weak justifications
                - Add missing edge case handling
                - Ensure final answer is an integer 000-999
                - Maintain step-by-step clarity""",
                context=f"Solution:\n{executions[i]}\n\nValidation Feedback:\n{validations[i]}"
            ) for i in range(len(executions))]
        )

        # PHASE 4: Consensus Synthesis and Final Refinement
        final_answer = await self.ensemble(
            instruction="""Synthesize these solution attempts into a single authoritative answer:
            - If all agree, select the common answer
            - If they disagree, identify the point of divergence and determine which approach is most mathematically sound
            - Prefer exact symbolic solutions over numerical approximations
            - Ensure answer satisfies ALL problem constraints
            - Format final answer as a 3-digit integer (000-999) with no units or explanation
            - If no solution is valid, return '000'""",
            contexts_list=revised_executions
        )

        # Final polish and formatting
        polished_answer = await self.revise(
            instruction="""Final verification and formatting:
            - Confirm answer is an integer between 000 and 999
            - Remove all explanatory text, units, or markdown
            - Return ONLY the 3-digit number as a string
            - If answer has fewer than 3 digits, pad with leading zeros""",
            context=final_answer
        )

        return polished_answer.strip()