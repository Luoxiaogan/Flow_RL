# Workflow ID: hotpotqa_34_0
# Benchmark: hotpotqa
# Data Indices: [41, 468]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - What entities are mentioned in the question?
            - What relationships or properties are being queried?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Document Processing - Extract entities and relationships from each document
        documents = self.problem_text.split("**QUESTION:**")[0].split("**CONTEXT DOCUMENTS:**")[1].strip().split("Document ")[1:]
        document_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from this document:
                - Identify people, places, organizations, and other key entities.
                - Highlight relationships between entities.
                - Focus on information relevant to the question: {initial_analysis}""",
                context=doc
            ) for doc in documents
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Identify Bridge Entities - Find entities that connect documents
        bridge_entities = await self.generate(
            instruction=f"""Identify bridge entities that connect the documents:
            - Look for shared entities across document analyses: {document_results}
            - Prioritize entities mentioned in the question: {initial_analysis}""",
            context=""
        )

        # Step 4: Construct Reasoning Chains - Build chains connecting entities across documents
        reasoning_chains = []
        for entity in bridge_entities.split(","):
            chain = await self.generate(
                instruction=f"""Build a reasoning chain starting with this entity: {entity.strip()}
                - Connect entities and relationships across documents.
                - Ensure each step is factually supported by the documents: {document_results}
                - End the chain with a potential answer to the question: {initial_analysis}""",
                context=""
            )
            reasoning_chains.append(chain)

        # Step 5: Ensemble - Evaluate and select the best reasoning chain
        best_chain = await self.ensemble(
            instruction=f"""Evaluate the reasoning chains and select the most promising one:
            - Check factual accuracy against the documents: {document_results}
            - Ensure the chain leads to a precise answer.
            - Prioritize chains that fully address the question: {initial_analysis}""",
            contexts_list=reasoning_chains
        )

        # Step 6: Answer Extraction - Extract the precise answer from the final document
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            - Use exact text spans from the documents.
            - Ensure the answer matches the expected format: {initial_analysis}
            - Link the answer to supporting facts in the documents: {best_chain}""",
            context=""
        )

        # Step 7: Iterative Refinement (Optional) - Refine the answer if necessary
        refined_answer = await self.revise(
            instruction=f"""Refine the answer for clarity and precision:
            - Ensure the answer is factually correct.
            - Verify supporting facts are explicitly linked to document sentences.
            - Improve any ambiguities or inconsistencies.""",
            context=answer
        )

        return refined_answer