# Workflow ID: hotpotqa_157_0
# Benchmark: hotpotqa
# Data Indices: [37, 286]

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

        # Step 1: Classify the question type
        classification = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining facts)?
            Provide a clear classification.""",
            context=""
        )

        # Step 2: Extract relevant entities and documents
        entities_and_documents = await self.generate(
            instruction=f"""Extract entities and relevant documents:
            - Identify key entities mentioned in the question.
            - Find these entities in the provided documents.
            - Extract sentences or paragraphs containing the entities.
            Question Type: {classification}""",
            context=""
        )

        # Step 3: Build reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Build a reasoning chain using the following information:
                - Entities: {entity}
                - Documents: {doc}
                Follow the chain to connect information across documents.""",
                context=entities_and_documents
            ) for entity, doc in parse_entities(entities_and_documents)]
        )
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain.",
            contexts_list=reasoning_chains
        )

        # Step 4: Extract and validate the answer
        raw_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Locate the exact sentence or phrase containing the answer.
            - Ensure the answer matches the question type: {classification}.
            Reasoning Chain: {best_chain}""",
            context=""
        )
        refined_answer = await self.revise(
            instruction="Validate and refine the answer for clarity and accuracy.",
            context=raw_answer
        )

        # Step 5: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Condense the answer into a short, factual response.",
            context=refined_answer
        )

        return final_answer