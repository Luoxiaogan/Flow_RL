# Workflow ID: hotpotqa_10_0
# Benchmark: hotpotqa
# Data Indices: [331, 299]

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

        # Step 1: Analyze the problem and classify question type
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining facts)?
            Provide structured classification and identify key entities.""",
            context=""
        )

        # Step 2: Extract entities from documents and question
        entities = await self.generate(
            instruction=f"""Extract all named entities from the documents and question:
            - Entities in the question: {analysis}
            - Entities in documents: Find mentions of these entities in the provided documents.
            Return entities as a structured list with their contexts.""",
            context=analysis
        )

        # Step 3: Identify potential bridge entities (parallel exploration)
        bridge_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze entity '{entity}' as a potential bridge:
                - Does it appear in multiple documents?
                - What connections does it establish?
                - How relevant is it to the question?""",
                context=entities
            ) for entity in entities.split('\n')]
        )

        # Step 4: Build reasoning chains for each candidate
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Build a reasoning chain for entity '{candidate}':
                - Start from the question.
                - Follow connections across documents.
                - Identify supporting facts for each step.""",
                context=candidate
            ) for candidate in bridge_candidates]
        )

        # Step 5: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Select the most supported reasoning chain:
            - Evaluate completeness of connections.
            - Check alignment with the question.
            - Prioritize chains with clear supporting facts.""",
            contexts_list=reasoning_chains
        )

        # Step 6: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Extract the exact answer from the final document:
            - Reasoning chain: {best_chain}
            - Expected format: Short text span or yes/no.
            Return the answer with supporting sentence(s).""",
            context=best_chain
        )

        # Step 7: Validate and refine the answer
        refined_answer = await self.revise(
            instruction="""Validate the answer:
            - Does it match the expected format?
            - Are all supporting facts correct?
            - Refine if necessary.""",
            context=answer
        )

        return refined_answer