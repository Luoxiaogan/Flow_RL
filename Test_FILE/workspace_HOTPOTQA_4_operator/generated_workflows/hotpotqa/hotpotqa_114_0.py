# Workflow ID: hotpotqa_114_0
# Benchmark: hotpotqa
# Data Indices: [47]

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
        import re

        # Step 1: Initial Analysis - Classify question type and identify entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Identify key entities and relationships mentioned in the question.
            3. Provide a structured summary of the analysis.""",
            context=""
        )

        # Step 2: Parallel Entity and Relationship Extraction
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract all entities and relationships from the following document:
                {doc}
                Focus on entities and relationships relevant to the question type identified earlier.""",
                context=initial_analysis
            )
            for doc in documents
        ]
        extracted_info = await asyncio.gather(*extraction_tasks)

        # Step 3: Relevance Scoring - Score documents based on extracted entities
        scoring_tasks = [
            self.generate(
                instruction=f"""Score the relevance of the following document to the question:
                Document: {doc}
                Entities: {info}
                Focus on how well the entities connect to the question.""",
                context=initial_analysis
            )
            for doc, info in zip(documents, extracted_info)
        ]
        relevance_scores = await asyncio.gather(*scoring_tasks)

        # Step 4: Reasoning Chain Construction - Synthesize information
        reasoning_chain = await self.ensemble(
            instruction="""Construct a reasoning chain by synthesizing information from relevant documents:
            - Connect entities across documents.
            - Ensure logical consistency.
            - Highlight supporting facts.""",
            contexts_list=extracted_info
        )

        # Step 5: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short factual span directly supported by the documents.""",
            context=reasoning_chain
        )
        validated_answer = await self.revise(
            instruction="""Validate the answer against the original documents:
            - Verify factual accuracy.
            - Ensure the answer matches the expected format.""",
            context=answer
        )

        return validated_answer