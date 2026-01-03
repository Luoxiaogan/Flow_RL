# Workflow ID: hotpotqa_67_0
# Benchmark: hotpotqa
# Data Indices: [368]

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

        # Step 1: Analyze the problem structure
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the question type (bridge, comparison, compositional).
            - Identify key entities and relationships.
            - Highlight any explicit constraints.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel exploration of documents
        entities = await self.generate(
            instruction="Extract named entities and relationships from the problem.",
            context=analysis
        )
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"Summarize this document focusing on entities: {entities}",
                context=document
            ) for document in self.extract_documents()]
        )

        # Step 3: Build reasoning chains
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from summaries:
            - Identify shared entities and relationships.
            - Build a logical chain connecting documents.
            - Resolve any conflicts or ambiguities.""",
            contexts_list=document_summaries
        )

        # Step 4: Extract and validate the answer
        raw_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Chain: {reasoning_chain}
            Ensure the answer matches the expected format.""",
            context=""
        )
        refined_answer = await self.revise(
            instruction="Refine the answer for factual correctness and clarity.",
            context=raw_answer
        )

        return refined_answer

    def extract_documents(self):
        """Helper function to extract document texts from the problem."""
        # Placeholder implementation
        return ["Document 1 text", "Document 2 text", "Document 3 text"]