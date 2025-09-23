# Workflow ID: hotpotqa_252_0
# Benchmark: hotpotqa
# Data Indices: [274, 118]

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
            instruction="""Classify the question into one of these types:
            - Bridge: Requires connecting entities across documents.
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts.
            Provide a clear explanation for your classification.""",
            context=""
        )

        # Step 2: Extract key entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all key entities and relationships from the question:
            Classification: {classification}
            
            Focus on:
            - Named entities (people, places, organizations)
            - Numbers and dates
            - Relationships between entities""",
            context=""
        )
        refined_entities = await self.revise(
            instruction="Refine the extracted entities to ensure accuracy and completeness.",
            context=entities
        )

        # Step 3: Analyze documents in parallel
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for information related to the entities:
                Entities: {refined_entities}
                
                Identify:
                - Relevant sentences
                - Supporting facts
                - Connections to other documents""",
                context=doc
            ) for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document ")[1:]]
        )

        # Step 4: Synthesize reasoning chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize the findings from all documents into a coherent reasoning chain:
            Entities: {refined_entities}
            
            Focus on:
            - Connecting supporting facts
            - Building logical bridges between documents
            - Ensuring factual consistency""",
            contexts_list=document_analyses
        )

        # Step 5: Extract and validate the answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            
            Ensure:
            - The answer is concise
            - It matches the expected format
            - It is directly supported by the documents""",
            context=reasoning_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the answer against the original documents to ensure factual correctness.",
            context=answer
        )

        return validated_answer