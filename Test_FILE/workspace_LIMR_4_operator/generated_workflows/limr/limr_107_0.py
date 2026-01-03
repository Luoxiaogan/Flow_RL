# Workflow ID: limr_107_0
# Benchmark: limr
# Data Indices: [228, 257]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and classify its type:
            - Identify key components (e.g., variables, constraints, objectives)
            - Classify the problem domain (e.g., algebraic, geometric, combinatorial)
            - Outline potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Solve the problem using an algebraic approach:
                - Derive equations
                - Perform calculations
                - Verify intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Solve the problem using a combinatorial approach:
                - Count possibilities
                - Apply constraints
                - Validate logic""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Solve the problem using a geometric approach:
                - Analyze figures
                - Apply geometric principles
                - Verify calculations""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement
        refined_approaches = []
        for approach in approaches:
            refined = await self.revise(
                instruction="Critique and improve this solution attempt. Ensure all steps are clear, logical, and error-free.",
                context=approach
            )
            refined_approaches.append(refined)

        # Step 4: Synthesis
        final_solution = await self.ensemble(
            instruction="Select the best solution or synthesize insights from multiple approaches. Ensure the final answer is precise and formatted correctly.",
            contexts_list=refined_approaches
        )

        # Step 5: Final Formatting
        formatted_solution = await self.summarize(
            instruction="Condense the final solution into a precise format. Ensure the answer is an integer between 000 and 999.",
            context=final_solution
        )

        return formatted_solution