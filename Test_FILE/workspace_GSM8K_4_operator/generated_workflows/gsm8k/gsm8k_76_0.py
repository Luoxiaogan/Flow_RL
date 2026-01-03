# Workflow ID: gsm8k_76_0
# Benchmark: gsm8k
# Data Indices: [65, 55]

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

        # Initial analysis to extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and identify:
            - All numerical values and their context
            - The type of problem (sequential, rate, distribution, proportion, multi-entity)
            - What the question is asking for
            Provide structured output.""",
            context=""
        )

        # Generate multiple solution paths if necessary
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Based on the analysis: {initial_analysis}\nDevelop a solution path focusing on sequential operations...",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Based on the analysis: {initial_analysis}\nDevelop a solution path focusing on rate problems...",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Based on the analysis: {initial_analysis}\nDevelop a solution path focusing on distribution and proportions...",
                context=initial_analysis
            )
        )

        # Validate and refine each solution path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine the solution path. Ensure all steps are accurate and logical.",
                context=path
            ) for path in solution_paths]
        )

        # Sequential calculation with intermediate validation
        final_results = []
        for path in refined_paths:
            steps = path.split('\n')
            intermediate_result = ""
            for step in steps:
                calculation = await self.generate(
                    instruction=f"Perform the calculation: {step}\nEnsure numerical accuracy and track units.",
                    context=intermediate_result
                )
                validation = await self.revise(
                    instruction="Check the calculation for errors and logical consistency.",
                    context=calculation
                )
                if "error" in validation.lower():
                    calculation = await self.revise(
                        instruction=f"Correct the error: {validation}",
                        context=calculation
                    )
                intermediate_result = calculation
            final_results.append(intermediate_result)

        # Final synthesis to select the best result
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete solution from the refined paths.",
            contexts_list=final_results
        )

        # Summarize the final answer
        summarized_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_answer
        )

        return summarized_answer