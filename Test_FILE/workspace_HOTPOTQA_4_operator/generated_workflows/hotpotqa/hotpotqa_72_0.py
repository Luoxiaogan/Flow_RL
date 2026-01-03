# Workflow ID: hotpotqa_72_0
# Benchmark: hotpotqa
# Data Indices: [339, 134]

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

        # Stage 1: Problem Analysis
        question_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities and relationships.
            3. Determine what information is needed to answer the question.
            Provide structured output.""",
            context=""
        )

        # Stage 2: Document Analysis (Parallel)
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0]
        doc_texts = [doc.strip() for doc in documents.split("Document")[1:] if doc.strip()]

        async def analyze_document(doc):
            return await self.generate(
                instruction=f"""Extract entities, relationships, and key facts from this document:
                {doc}
                Format as structured list.""",
                context=""
            )

        doc_analyses = await asyncio.gather(*[analyze_document(doc) for doc in doc_texts])

        # Stage 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities connecting documents:
            - Entities mentioned in multiple documents
            - Relationships between entities
            Rank entities by relevance to the question.""",
            contexts_list=doc_analyses
        )

        # Stage 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain using the bridge entities:
            Bridge Entities: {bridge_entities}
            Documents: {documents}
            Follow logical connections to derive the answer.""",
            context=question_analysis
        )

        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity and logical consistency.",
            context=reasoning_chain
        )

        # Stage 5: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            Reasoning Chain: {refined_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=""
        )

        answer_validation = await self.ensemble(
            instruction="""Validate the answer against supporting facts:
            - Is it factually correct?
            - Is it supported by evidence from multiple documents?""",
            contexts_list=[answer_extraction, *doc_analyses]
        )

        # Stage 6: Conditional Handling
        if "insufficient evidence" in answer_validation.lower():
            fallback_answer = await self.generate(
                instruction="Explore alternative interpretations or request clarification.",
                context=answer_validation
            )
            return fallback_answer

        return answer_validation