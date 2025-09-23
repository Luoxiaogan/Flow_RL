# Workflow ID: limr_73_0
# Benchmark: limr
# Data Indices: [233, 114]

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

        # Phase 1: Problem Analysis and Decomposition
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (numerical, logical, geometric, etc.)
            - Extract key entities, numbers, and relationships
            - Highlight constraints and conditions
            - Determine the expected answer format""",
            context=""
        )
        problem_summary = await self.summarize(
            instruction="Condense the analysis into a structured summary.",
            context=analysis
        )

        # Phase 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt a solution using algebraic methods:
                - Apply equations and transformations
                - Show all intermediate steps
                - Verify calculations""",
                context=problem_summary
            ),
            self.generate(
                instruction=f"""Attempt a solution using combinatorial methods:
                - Use counting principles and permutations
                - Consider edge cases and special scenarios
                - Justify each step""",
                context=problem_summary
            ),
            self.generate(
                instruction=f"""Attempt a solution using geometric reasoning:
                - Visualize shapes and spatial relationships
                - Use trigonometric identities and vector calculations
                - Ensure consistency with constraints""",
                context=problem_summary
            )
        )
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Refine the solution attempt by verifying steps and correcting errors.",
                context=strategy
            ) for strategy in strategies]
        )

        # Phase 3: Ensemble Synthesis
        ensemble_solution = await self.ensemble(
            instruction="Evaluate and synthesize the refined strategies into a unified solution.",
            contexts_list=refined_strategies
        )
        final_solution = await self.summarize(
            instruction="Distill the ensemble solution into a concise answer.",
            context=ensemble_solution
        )

        # Phase 4: Adaptive Feedback Loop
        validation = await self.generate(
            instruction=f"""Validate the final solution against the original problem:
            - Check adherence to constraints
            - Verify intermediate steps
            - Confirm the answer format""",
            context=final_solution
        )
        if "error" in validation.lower():
            refined_final = await self.revise(
                instruction=f"Refine the solution based on validation feedback: {validation}",
                context=final_solution
            )
            return refined_final
        else:
            return final_solution