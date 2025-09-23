# Workflow ID: hotpotqa_294_0
# Benchmark: hotpotqa
# Data Indices: [31]

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
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Determine the expected answer format.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Parallel Exploration
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Explore entity-based connections:
                Using analysis: {analysis}
                Find shared entities between documents.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Explore property-based connections:
                Using analysis: {analysis}
                Compare properties across documents.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Explore contextual connections:
                Using analysis: {analysis}
                Infer relationships from contextual clues.""",
                context=analysis
            )
        )

        # Phase 3: Validation and Refinement
        refined_chains = []
        for chain in reasoning_chains:
            refined = await self.revise(
                instruction="""Validate and refine this reasoning chain:
                1. Check factual accuracy against documents.
                2. Ensure logical consistency.
                3. Improve clarity and precision.""",
                context=chain
            )
            refined_chains.append(refined)

        # Phase 4: Synthesis and Decision
        final_answer = await self.ensemble(
            instruction="""Select the best reasoning chain:
            1. Prioritize factual correctness.
            2. Ensure logical coherence.
            3. Extract precise answer span.""",
            contexts_list=refined_chains
        )

        return final_answer