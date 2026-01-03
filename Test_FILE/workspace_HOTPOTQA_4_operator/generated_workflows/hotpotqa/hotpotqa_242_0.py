# Workflow ID: hotpotqa_242_0
# Benchmark: hotpotqa
# Data Indices: [110]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities in the question.
            - Highlight potential bridge entities that connect documents.
            Provide a structured breakdown of the question.""",
            context=""
        )

        # Phase 2: Entity Linking and Document Connection
        # Generate summaries for each document and identify shared entities
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"Summarize the content of this document and identify key entities:\n{doc}",
                context=""
            ) for doc in self.extract_documents()]
        )
        # Synthesize summaries to find connections
        connections = await self.ensemble(
            instruction="Identify shared entities and connections between documents. Highlight potential bridge entities.",
            contexts_list=document_summaries
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = ""
        for entity in self.extract_bridge_entities(connections):
            link = await self.generate(
                instruction=f"""Using the entity '{entity}', construct a reasoning link:
                - Which documents are connected by this entity?
                - What facts support this connection?
                - How does this link contribute to answering the question?""",
                context=reasoning_chain
            )
            reasoning_chain += link + "\n"
        
        # Validate and refine the reasoning chain
        refined_chain = await self.revise(
            instruction="Ensure the reasoning chain is logically sound and factually correct. Fix any gaps or ambiguities.",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction
        answer = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {refined_chain}
            
            Extract the final answer from the relevant document. Ensure it is precise and matches the expected format.""",
            context=""
        )

        return answer

    def extract_documents(self):
        """Helper function to extract document texts from the problem."""
        # Placeholder implementation
        return ["Document 1 content...", "Document 2 content..."]

    def extract_bridge_entities(self, connections):
        """Helper function to extract bridge entities from connections."""
        # Placeholder implementation
        return ["Entity1", "Entity2"]