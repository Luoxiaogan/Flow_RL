# Workflow ID: hotpotqa_38_0
# Benchmark: hotpotqa
# Data Indices: [67]

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
        question_type = await self.generate(
            instruction="""Classify the question type:
            1. Bridge: Requires connecting information through shared entities (e.g., "What nationality is the director of [movie]?")
            2. Comparison: Involves comparing properties across documents (e.g., "Which was founded first, X or Y?")
            3. Compositional: Combines multiple facts to derive the answer
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and facts from all documents
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        document_texts = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        entity_extractions = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract named entities, key facts, and relationships from this document: {doc}",
                context=""
            ) for doc in document_texts]
        )
        all_entities = "\n".join(entity_extractions)

        # Step 3: Identify bridge entities (if applicable)
        if "bridge" in question_type.lower():
            bridge_entities = await self.ensemble(
                instruction="Identify shared entities that connect documents. Focus on entities mentioned in multiple documents.",
                contexts_list=entity_extractions
            )
        else:
            bridge_entities = ""

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain to answer the question:
            Question: {self.problem_text.split('**QUESTION:**')[1].split('**ANSWER:**')[0].strip()}
            Available Entities and Facts: {all_entities}
            Bridge Entities: {bridge_entities}
            Follow the reasoning chain step-by-step and justify each connection.""",
            context=""
        )

        # Step 5: Validate and refine reasoning chain
        refined_chain = await self.revise(
            instruction="Validate the reasoning chain for logical consistency and factual accuracy. Revise if necessary.",
            context=reasoning_chain
        )

        # Step 6: Extract precise answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            Reasoning Chain: {refined_chain}
            Ensure the answer is a short text span (entity/phrase) or yes/no response.""",
            context=""
        )

        # Step 7: Final validation
        final_answer = await self.revise(
            instruction="Validate the answer against the original question and documents. Refine if necessary.",
            context=answer
        )

        return final_answer