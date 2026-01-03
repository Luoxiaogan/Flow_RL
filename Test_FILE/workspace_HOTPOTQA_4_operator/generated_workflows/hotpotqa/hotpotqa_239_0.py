# Workflow ID: hotpotqa_239_0
# Benchmark: hotpotqa
# Data Indices: [384]

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

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the question to:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract all named entities (people, places, events).
            3. Identify constraints or conditions.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Parallel Document Exploration
        entities = await self.generate(
            instruction="Extract all named entities from the question.",
            context=analysis
        )
        document_tasks = [
            self.generate(
                instruction=f"Find entities matching '{entities}' in this document.",
                context=document
            ) for document in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Phase 3: Reasoning Chain Construction
        chain_candidates = []
        for result in document_results:
            chain = await self.generate(
                instruction=f"Construct a reasoning chain using entities from {result}.",
                context=result
            )
            refined_chain = await self.revise(
                instruction="Validate and refine the reasoning chain.",
                context=chain
            )
            chain_candidates.append(refined_chain)

        # Phase 4: Answer Extraction
        answer_candidates = []
        for chain in chain_candidates:
            answer = await self.generate(
                instruction="Extract the precise answer span from the relevant document.",
                context=chain
            )
            answer_candidates.append(answer)

        # Phase 5: Ensemble Decision
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer based on reasoning chain validity and factual support.",
            contexts_list=answer_candidates
        )

        return final_answer