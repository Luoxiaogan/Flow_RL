# Workflow ID: hotpotqa_264_0
# Benchmark: hotpotqa
# Data Indices: [423, 280]

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

        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem type:
            - Is it a bridge question (connecting entities)?
            - A comparison question (comparing properties)?
            - A compositional question (chaining facts)?
            Provide the type and any key entities or relationships.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        extraction = await self.generate(
            instruction=f"""Extract all entities, relationships, and constraints from the context documents:
            - Entities: People, places, organizations.
            - Relationships: Connections between entities.
            - Constraints: Temporal, spatial, logical.
            Use the classification: {classification}""",
            context=""
        )

        # Step 3: Build reasoning chains (parallel exploration)
        chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain for the question:
                - Start with the extracted entities and relationships: {extraction}
                - Follow the classification: {classification}
                - Ensure each step is supported by evidence from the documents.""",
                context=extraction
            ) for _ in range(3)]  # Explore up to 3 chains
        )

        # Step 4: Validate and refine chains
        validated_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this chain for logical consistency, factual accuracy, and completeness:
                - Chain: {chain}
                - Context: {extraction}""",
                context=chain
            ) for chain in chains]
        )

        # Step 5: Select the best chain
        best_chain = await self.ensemble(
            instruction="""Select the best reasoning chain:
            - Prioritize chains with strong evidence and direct connections to the question.
            - Discard invalid or incomplete chains.""",
            contexts_list=validated_chains
        )

        # Step 6: Extract the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            - Use the best chain: {best_chain}
            - Return the exact text span or yes/no response.""",
            context=best_chain
        )

        return answer