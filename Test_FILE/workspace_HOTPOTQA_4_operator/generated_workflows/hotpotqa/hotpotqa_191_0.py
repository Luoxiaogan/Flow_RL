# Workflow ID: hotpotqa_191_0
# Benchmark: hotpotqa
# Data Indices: [230]

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
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting documents through shared entities.
            2. Comparison Question: Involves comparing properties across documents.
            3. Compositional Question: Demands combining multiple facts to derive an answer.
            Provide the classification label and a brief rationale.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_parts = documents.split("Document ")[1:]
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from the following document:
                {doc_part}
                Format as a structured list with categories: People, Places, Organizations, Relationships.""",
                context=""
            )
            for doc_part in doc_parts
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Identify bridge entity or comparable attributes
        if "Bridge Question" in classification:
            bridge_entity = await self.ensemble(
                instruction="Identify shared entities across documents.",
                contexts_list=extracted_entities
            )
        elif "Comparison Question" in classification:
            comparable_attributes = await self.ensemble(
                instruction="Extract comparable attributes (e.g., dates, quantities) from the relevant documents.",
                contexts_list=extracted_entities
            )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Build a reasoning chain to answer the question:
            Classification: {classification}
            Extracted Entities: {extracted_entities}
            Bridge Entity/Comparable Attributes: {bridge_entity if 'Bridge Question' in classification else comparable_attributes}
            Trace the logical flow from the question to the answer.""",
            context=""
        )

        # Step 5: Extract precise answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=""
        )

        # Step 6: Validate and refine
        refined_answer = await self.revise(
            instruction=f"""Validate the reasoning chain and answer:
            Reasoning Chain: {reasoning_chain}
            Answer: {answer}
            Check for logical consistency, factual accuracy, and adherence to the question's requirements.""",
            context=reasoning_chain
        )

        return refined_answer