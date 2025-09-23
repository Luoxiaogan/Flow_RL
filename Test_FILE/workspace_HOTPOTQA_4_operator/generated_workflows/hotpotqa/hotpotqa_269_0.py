# Workflow ID: hotpotqa_269_0
# Benchmark: hotpotqa
# Data Indices: [375, 434]

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
        analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            1. Is this a bridge, comparison, or compositional question?
            2. Extract all named entities (people, places, organizations).
            3. Identify relationships between entities.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore reasoning chains
        if "bridge" in analysis.lower():
            # Bridge question: Identify shared entities and follow relationships
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Follow the relationship for entity: {entity}.
                    Identify connected documents and extract relevant facts.""",
                    context=analysis
                ) for entity in analysis.split("\n") if "entity" in entity.lower()]
            )
        elif "comparison" in analysis.lower():
            # Comparison question: Extract comparable properties
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Extract property: {property}.
                    Identify comparable values across documents.""",
                    context=analysis
                ) for property in analysis.split("\n") if "property" in property.lower()]
            )
        else:
            # Default: General exploration
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Explore reasoning chain for: {item}.""",
                    context=analysis
                ) for item in analysis.split("\n")]
            )

        # Step 3: Validation and Refinement
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine reasoning chain:
                Ensure logical consistency and alignment with question requirements.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 4: Synthesis and Answer Extraction
        synthesis = await self.ensemble(
            instruction="""Synthesize reasoning chains into a single coherent answer:
            1. Select the most plausible chain.
            2. Extract the precise answer span from the relevant document.""",
            contexts_list=refined_chains
        )

        return synthesis