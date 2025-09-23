# Workflow ID: gsm8k_91_0
# Benchmark: gsm8k
# Data Indices: [62, 209]

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

        # Initial Analysis: Extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it:
            - Identify all numerical values and their context
            - Determine what the question asks for
            - Classify the problem type (sequential, rate, distribution, proportion, multi-entity)
            - Highlight any implicit constraints or assumptions""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop an estimation-based solution based on: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a logical reasoning solution based on: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Refinement: Validate and improve each approach
        refined_approaches = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine the following solution: {approach}",
                context=approach
            ) for approach in approaches]
        )

        # Summarization: Compress refined approaches to key points
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"Summarize the key points of the following solution: {refined}",
                context=refined
            ) for refined in refined_approaches]
        )

        # Ensemble: Synthesize the best solution from the summaries
        final_solution = await self.ensemble(
            instruction="Synthesize the most accurate and complete solution from the provided summaries",
            contexts_list=summaries
        )

        # Final Validation: Ensure the solution meets all requirements
        validated_solution = await self.revise(
            instruction=f"Perform final validation on the solution: {final_solution}. Ensure it addresses all parts of the problem and provides a numerically exact answer.",
            context=final_solution
        )

        # Extract the final numerical answer
        final_answer = await self.generate(
            instruction=f"Extract the final numerical answer from the validated solution: {validated_solution}. Ensure it is presented as a single value.",
            context=validated_solution
        )

        return final_answer.strip()