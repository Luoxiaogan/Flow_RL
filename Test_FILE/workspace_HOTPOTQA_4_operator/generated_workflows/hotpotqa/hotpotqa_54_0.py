# Workflow ID: hotpotqa_54_0
# Benchmark: hotpotqa
# Data Indices: [391, 247]

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
            instruction="""Analyze the question:
            1. Classify it as bridge, comparison, or compositional.
            2. Extract all named entities (people, places, organizations).
            3. Identify relationships between entities.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Document Analysis
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0]
        doc_tasks = [
            self.generate(
                instruction=f"""Analyze this document:
                1. Identify mentions of entities from the question.
                2. Highlight shared entities with other documents.
                Document content: {doc}""",
                context=analysis
            ) for doc in documents.split("Document ")[1:]
        ]
        doc_results = await asyncio.gather(*doc_tasks)
        relevant_docs = await self.ensemble(
            instruction="Identify documents most relevant to the question.",
            contexts_list=doc_results
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct reasoning chain:
            1. Use entities and relationships from analysis.
            2. Connect information across relevant documents: {relevant_docs}.
            Provide step-by-step reasoning.""",
            context=analysis
        )
        refined_chain = await self.revise(
            instruction="Refine reasoning chain for clarity and completeness.",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction
        answer = await self.summarize(
            instruction=f"""Extract precise answer:
            1. Locate exact sentence or phrase supporting the answer.
            2. Ensure it is concise and factual.
            Reasoning chain: {refined_chain}""",
            context=relevant_docs
        )

        # Phase 5: Validation and Refinement
        final_answer = await self.revise(
            instruction="Validate answer against question and refine if necessary.",
            context=answer
        )

        return final_answer