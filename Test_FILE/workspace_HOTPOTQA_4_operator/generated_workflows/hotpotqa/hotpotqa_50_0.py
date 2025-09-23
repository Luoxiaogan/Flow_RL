# Workflow ID: hotpotqa_50_0
# Benchmark: hotpotqa
# Data Indices: [149, 281]

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

        # Step 1: Analyze the problem and classify the question type
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities or concepts mentioned in the question.
            3. Determine the expected answer format (short phrase, yes/no).
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Extract entities and facts from all documents
        documents = await self.generate(
            instruction=f"""Extract key entities, relationships, and facts from all documents:
            - Focus on entities mentioned in the question: {analysis}
            - Include metadata such as titles and sentence IDs for reference.
            Format as a structured list with document titles as keys.""",
            context=""
        )

        # Step 3: Identify bridge entities and potential reasoning chains
        bridge_entities = await self.generate(
            instruction=f"""Identify bridge entities that connect documents:
            - Use the extracted entities and facts: {documents}
            - Find shared names, dates, or other common attributes.
            - Propose multiple candidate reasoning chains if applicable.
            Format as a list of chains, each with supporting facts.""",
            context=documents
        )

        # Step 4: Evaluate and synthesize reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate reasoning chain:
                - Check factual correctness of each step.
                - Ensure coherence and logical flow.
                Chain: {chain}""",
                context=documents
            ) for chain in bridge_entities.split('\n\n')]
        )
        best_chain = await self.ensemble(
            instruction="Select the most coherent and factually supported reasoning chain.",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the precise answer span
        answer_span = await self.generate(
            instruction=f"""Extract the exact answer span from the final document in the reasoning chain:
            - Use the selected chain: {best_chain}
            - Ensure the answer matches the expected format (short phrase, yes/no).
            - Include supporting sentence IDs for verification.""",
            context=documents
        )

        # Step 6: Validate the answer
        validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Check factual correctness against the question and documents.
            - Ensure the answer is supported by the reasoning chain.
            - Suggest refinements if necessary.
            Answer: {answer_span}""",
            context=best_chain
        )

        # Step 7: Return the final answer
        return validation