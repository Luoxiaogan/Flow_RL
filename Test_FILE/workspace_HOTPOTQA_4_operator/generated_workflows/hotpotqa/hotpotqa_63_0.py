# Workflow ID: hotpotqa_63_0
# Benchmark: hotpotqa
# Data Indices: [81]

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

        # Initial analysis to classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to:
            1. Identify all named entities, numbers, and relationships.
            2. Classify the question type (bridge, comparison, compositional).
            3. Highlight potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Parallel processing to extract relevant facts from each document
        documents = self.problem_text.split('Document ')[1:]  # Split by document
        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract key facts and entities from Document {i}. Focus on entities related to: {initial_analysis}",
                context=doc
            ) for i, doc in enumerate(documents, start=1)]
        )

        # Identify bridge entities and build reasoning chains
        bridge_entities = await self.ensemble(
            instruction=f"""Identify bridge entities that connect documents:
            Documents: {documents}
            Extracted Facts: {document_facts}
            Use these entities to construct reasoning chains across documents.""",
            contexts_list=document_facts
        )

        # Extract potential answers based on reasoning chains
        potential_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"Using reasoning chain: {bridge_entities}, extract potential answers from Document {i}.",
                context=doc
            ) for i, doc in enumerate(documents, start=1)]
        )

        # Refine answers for precision and factual correctness
        refined_answers = await asyncio.gather(
            *[self.revise(
                instruction=f"Ensure the answer is precise and factually correct. Context: {answer}",
                context=answer
            ) for answer in potential_answers]
        )

        # Final synthesis to select the best answer
        final_answer = await self.ensemble(
            instruction=f"""Select the most accurate answer supported by evidence from different documents:
            Refined Answers: {refined_answers}
            Bridge Entities: {bridge_entities}""",
            contexts_list=refined_answers
        )

        return final_answer