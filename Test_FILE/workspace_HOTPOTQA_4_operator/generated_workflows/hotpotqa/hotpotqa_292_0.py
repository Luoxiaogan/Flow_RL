# Workflow ID: hotpotqa_292_0
# Benchmark: hotpotqa
# Data Indices: [236]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Identify potential bridge entities connecting documents.
            Provide structured output.""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Refine the classification and ensure completeness.",
            context=initial_analysis
        )

        # Step 2: Entity Exploration - Explore relationships in parallel
        entities = [e.strip() for e in refined_analysis.split("\n") if e.strip()]
        entity_explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"Explore relationships for entity: {entity}. "
                            f"Find connections across documents.",
                context=refined_analysis
            ) for entity in entities]
        )
        unified_chains = await self.ensemble(
            instruction="Synthesize findings into unified reasoning chains.",
            contexts_list=entity_explorations
        )

        # Step 3: Chain Validation - Iteratively validate chains
        reasoning_chains = unified_chains.split("\n")
        valid_chains = []
        for chain in reasoning_chains:
            validation = await self.generate(
                instruction=f"Validate this reasoning chain: {chain}. "
                            f"Cross-reference with original documents.",
                context=refined_analysis
            )
            if "valid" in validation.lower():
                valid_chains.append(chain)

        # Step 4: Answer Extraction - Extract and summarize the answer
        if not valid_chains:
            return "Insufficient information to derive an answer."

        final_chain = valid_chains[0]  # Choose the first valid chain
        answer_extraction = await self.generate(
            instruction=f"Extract the precise answer from the final document in this chain: {final_chain}.",
            context=refined_analysis
        )
        summarized_answer = await self.summarize(
            instruction="Condense the answer into a short factual response.",
            context=answer_extraction
        )

        return summarized_answer