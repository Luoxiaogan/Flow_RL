# Workflow ID: hotpotqa_243_0
# Benchmark: hotpotqa
# Data Indices: [330]

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
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and identify potential bridge entities or relationships. Extract key entities 
            and their roles from the documents.""",
            context=""
        )

        # Step 2: Parallel Exploration
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the following analysis: {initial_analysis}
                Generate a reasoning chain connecting facts from at least two documents.
                Focus on the first bridge entity.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the following analysis: {initial_analysis}
                Generate a reasoning chain connecting facts from at least two documents.
                Focus on the second bridge entity.""",
                context=initial_analysis
            )
        )

        # Step 3: Reasoning Chain Refinement
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Refine the reasoning chain: ensure logical consistency, 
                factual accuracy, and connection to the original question.",
                context=path
            ) for path in reasoning_paths]
        )

        # Step 4: Answer Synthesis
        final_answer = await self.ensemble(
            instruction="""Combine the refined reasoning chains into a single, 
            coherent answer. Ensure the answer is supported by evidence from multiple 
            documents and matches the expected format (short text spans or yes/no).""",
            contexts_list=refined_chains
        )

        # Step 5: Final Validation
        validated_answer = await self.generate(
            instruction=f"""Validate the final answer: {final_answer}
            Ensure it directly addresses the original question and is factually 
            correct based on the provided documents.""",
            context=final_answer
        )

        return validated_answer