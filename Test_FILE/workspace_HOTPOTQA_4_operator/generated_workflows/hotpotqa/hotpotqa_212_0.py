# Workflow ID: hotpotqa_212_0
# Benchmark: hotpotqa
# Data Indices: [30, 386]

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
        analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional):
            1. Identify key entities and relationships in the question.
            2. Determine which documents are likely relevant.
            3. Provide structured classification and entity list.""",
            context=""
        )

        # Phase 2: Document Filtering and Entity Mapping
        entities = await self.generate(
            instruction=f"""Extract sentences containing key entities from relevant documents:
            Entities: {analysis}
            Focus on sentences that directly mention the entities and provide useful information.""",
            context=""
        )
        filtered_docs = await asyncio.gather(
            *[self.generate(
                instruction=f"Filter document {i} for relevance to entities: {entities}",
                context=""
            ) for i in range(10)]  # Assuming up to 10 documents
        )

        # Phase 3: Reasoning Chain Refinement
        reasoning_chain = await self.revise(
            instruction=f"""Refine the reasoning chain:
            Entities: {entities}
            Documents: {filtered_docs}
            Ensure logical flow and factual support for each step.""",
            context=filtered_docs
        )

        # Phase 4: Answer Extraction and Validation
        answer_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract precise answer span from document {i} based on reasoning chain: {reasoning_chain}",
                context=doc
            ) for i, doc in enumerate(filtered_docs)]
        )

        # Phase 5: Ensemble Decision
        final_answer = await self.ensemble(
            instruction=f"""Select the best answer based on evidence strength and alignment with reasoning chain:
            Candidates: {answer_candidates}
            Reasoning Chain: {reasoning_chain}""",
            contexts_list=answer_candidates
        )

        return final_answer