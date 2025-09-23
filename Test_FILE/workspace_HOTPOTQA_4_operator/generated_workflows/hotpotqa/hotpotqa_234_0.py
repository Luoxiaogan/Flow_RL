# Workflow ID: hotpotqa_234_0
# Benchmark: hotpotqa
# Data Indices: [138]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Connects entities across documents (e.g., "What nationality is the director of [movie]?")
            2. Comparison Question: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            3. Compositional Question: Combines multiple facts to derive an answer
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_relationships = await self.generate(
            instruction=f"""Extract all named entities and their relationships from the documents:
            - Entities: People, places, organizations, etc.
            - Relationships: Connections between entities (e.g., "directed," "starred in")
            Prioritize entities relevant to the question type: {question_type}""",
            context=""
        )

        # Step 3: Build reasoning chains (parallel processing for efficiency)
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using the following entities and relationships:
                {entities_relationships}
                Ensure the chain connects at least two documents and leads to a potential answer.""",
                context=""
            ) for _ in range(3)]  # Generate multiple chains for robustness
        )

        # Step 4: Validate and refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the reasoning chain:
                - Check for logical consistency
                - Verify factual accuracy
                - Identify missing links
                Refine the chain if necessary.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Select the most robust reasoning chain based on:
            - Logical consistency
            - Factual accuracy
            - Completeness of information""",
            contexts_list=refined_chains
        )

        # Step 6: Extract the precise answer
        answer = await self.summarize(
            instruction=f"""Extract the exact answer from the reasoning chain:
            {best_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=best_chain
        )

        return answer