# Workflow ID: gsm8k_136_0
# Benchmark: gsm8k
# Data Indices: [118, 108]

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
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Step 1: Initial Analysis - Extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numerical values and their units
            - Identify relationships between numbers (e.g., rates, proportions)
            - Classify the problem type (e.g., sequential, rate, distribution, proportion)
            - Highlight any ambiguities or missing information""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction="Propose a solution using sequential arithmetic operations...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Propose a solution using proportional reasoning...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Propose a solution using rate-based calculations...",
                context=initial_analysis
            )
        )

        # Step 3: Summarize Each Approach - Condense outputs for clarity
        summarized_approaches = await asyncio.gather(
            *[self.summarize(
                instruction="Condense this approach into key steps and results...",
                context=approach
            ) for approach in approaches]
        )

        # Step 4: Ensemble - Select the best approach or synthesize a unified solution
        selected_solution = await self.ensemble(
            instruction="""Evaluate and select the best approach:
            - Consider logical consistency
            - Check for completeness
            - Prefer exact calculations over approximations""",
            contexts_list=summarized_approaches
        )

        # Step 5: Iterative Refinement - Validate and refine the selected solution
        refined_solution = selected_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the solution for accuracy and completeness...",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Correct the following issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Final Answer Extraction - Extract the numerical result
        final_answer = await self.generate(
            instruction="Extract the final numerical answer from the refined solution...",
            context=refined_solution
        )

        return final_answer