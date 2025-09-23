# Workflow ID: hotpotqa_175_0
# Benchmark: hotpotqa
# Data Indices: [141]

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

        # Step 1: Initial Analysis - Identify question type and key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify as bridge, comparison, or compositional.
            2. Extract all named entities, numbers, and relationships.
            3. Identify potential bridge entities connecting documents.
            Provide structured classification and entity list.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Extract relevant information
        documents = [f"Document {i+1}" for i in range(10)]  # Assuming up to 10 documents
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""From {doc}:
                1. Extract key facts related to entities from initial analysis.
                2. Highlight potential bridge connections.
                3. Summarize relevant content.""",
                context=initial_analysis
            ) for doc in documents]
        )

        # Step 3: Reasoning Chain Construction - Build connections
        reasoning_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Using extracted facts from {documents[i]}:
                1. Connect entities across documents.
                2. Build logical reasoning chains.
                3. Validate connections with supporting facts.""",
                context=doc_analysis
            ) for i, doc_analysis in enumerate(document_analyses)]
        )

        # Step 4: Answer Extraction and Validation - Ensure factual correctness
        potential_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""From reasoning chain:
                1. Extract precise answer spans.
                2. Validate factual correctness against original documents.
                3. Format answer according to requirements.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Final Synthesis - Combine insights into final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize all potential answers:
            1. Select most supported answer.
            2. Ensure consistency with question requirements.
            3. Present concise final response.""",
            contexts_list=potential_answers
        )

        return final_answer