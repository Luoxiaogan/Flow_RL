# Workflow ID: hotpotqa_134_0
# Benchmark: hotpotqa
# Data Indices: [380, 206]

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

        # Phase 1: Problem Decomposition
        problem_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify the question type (bridge, comparison, compositional).
            - Extract key entities mentioned in the question.
            - Determine the expected answer format.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Parallel Document Analysis
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_titles = [line.split(":")[0].strip() for line in documents.split("\n") if "Document" in line]
        doc_contents = documents.split("Document ")[1:]

        async def analyze_document(doc_content):
            return await self.generate(
                instruction=f"""Analyze this document:
                - Extract all named entities, relationships, and key facts.
                - Identify potential bridge entities related to the question.
                - Highlight sentences containing relevant information.
                Document content: {doc_content}""",
                context=problem_analysis
            )

        doc_analyses = await asyncio.gather(*[analyze_document(doc) for doc in doc_contents])

        # Phase 3: Entity Linking and Chain Formation
        linking_results = await self.generate(
            instruction=f"""Identify connections between documents:
            - Find shared entities or relationships across documents.
            - Construct reasoning chains that connect these entities.
            - Ensure the chain leads to an answer for the question.
            Document analyses: {doc_analyses}""",
            context=problem_analysis
        )

        # Phase 4: Answer Synthesis
        answer_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer span from this reasoning chain:
                - Focus on factual correctness.
                - Ensure the answer matches the expected format.
                Reasoning chain: {chain}""",
                context=linking_results
            ) for chain in linking_results.split("\n\n")]
        )

        # Phase 5: Validation and Refinement
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            - Evaluate factual correctness and relevance.
            - Prefer answers with clear supporting evidence.
            - Resolve any contradictions between candidates.""",
            contexts_list=answer_candidates
        )

        return final_answer