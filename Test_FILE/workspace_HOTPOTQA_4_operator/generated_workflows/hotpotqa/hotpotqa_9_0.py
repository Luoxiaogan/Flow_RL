# Workflow ID: hotpotqa_9_0
# Benchmark: hotpotqa
# Data Indices: [119]

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

        # Phase 1: Problem Analysis and Classification
        classification = await self.generate(
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (comparing properties across documents)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Phase 2: Entity and Relationship Extraction
        document_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all named entities and relationships from this document:
                - Entities: People, places, organizations, etc.
                - Relationships: How entities are connected
                Format as structured list.""",
                context=document
            ) for document in self.context_documents]
        )

        # Combine entities and relationships across documents
        combined_entities = await self.ensemble(
            instruction="Identify the most relevant entities and relationships that connect documents.",
            contexts_list=document_entities
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the following entities and relationships:
                {combined_entities}
                
                Construct a reasoning chain that connects the documents to answer the question:
                - Trace connections between entities
                - Synthesize relevant information
                Provide a detailed reasoning chain.""",
                context=entity
            ) for entity in combined_entities.split('\n')]
        )

        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Refine the reasoning chain for clarity and accuracy.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Phase 4: Answer Extraction and Validation
        answer_candidates = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Extract the precise answer from the reasoning chain:
                {chain}
                
                Ensure the answer is a short text span or yes/no response.""",
                context=chain
            ) for chain in refined_chains]
        )

        final_answer = await self.ensemble(
            instruction="Select the most accurate and concise answer based on supporting facts.",
            contexts_list=answer_candidates
        )

        return final_answer