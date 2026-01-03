# Workflow ID: gsm8k_89_0
# Benchmark: gsm8k
# Data Indices: [159, 216]

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

        # Step 1: Initial Analysis - Extract key components and classify the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify all numerical values and their units
            - Extract relationships and operations mentioned explicitly or implicitly
            - Classify the problem type (e.g., rate, distribution, proportion)
            - Highlight what the question is asking for
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Propose a solution path focusing on direct calculations:
                - Use the extracted information: {initial_analysis}
                - Build a step-by-step calculation chain
                - Show intermediate results explicitly""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Propose a solution path focusing on proportional reasoning:
                - Use the extracted information: {initial_analysis}
                - Identify ratios, fractions, or scaling factors
                - Build a step-by-step calculation chain
                - Show intermediate results explicitly""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Propose a solution path focusing on logical deduction:
                - Use the extracted information: {initial_analysis}
                - Deduce relationships and constraints
                - Build a step-by-step calculation chain
                - Show intermediate results explicitly""",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement - Validate and refine each solution path
        refined_paths = []
        for path in solution_paths:
            refined = await self.revise(
                instruction="""Review the solution path:
                - Check for logical consistency
                - Verify calculations
                - Clarify ambiguous steps
                - Ensure the final answer matches the question""",
                context=path
            )
            refined_paths.append(refined)

        # Step 4: Final Synthesis - Combine insights and select the best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the refined solution paths:
            - Compare logical consistency and accuracy
            - Select the most robust and clear solution
            - Ensure the final answer is numerically exact""",
            contexts_list=refined_paths
        )

        # Step 5: Condense Output - Summarize the final solution
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer:
            - Remove intermediate steps and explanations
            - Present only the final result""",
            context=final_solution
        )

        return final_answer