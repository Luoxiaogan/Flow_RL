# Workflow ID: hotpotqa_327_0
# Benchmark: hotpotqa
# Data Indices: [481, 71]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify key entities or relationships mentioned in the question.
            - List potential bridge entities that connect documents.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore reasoning paths for each entity
        entities = await self.generate(
            instruction="Extract all named entities and relationships from the context documents.",
            context=initial_analysis
        )
        reasoning_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using entity: {entity}, construct a reasoning chain:
                - Identify documents connected by this entity.
                - Extract relevant facts from these documents.
                - Build a logical flow to answer the question.""",
                context=entities
            ) for entity in entities.split("\n") if entity.strip()]
        )

        # Step 3: Validation and Refinement - Validate reasoning chains
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this reasoning chain:
                - Check factual accuracy of extracted information.
                - Ensure logical consistency across documents.
                - Highlight any missing or ambiguous steps.""",
                context=path
            ) for path in reasoning_paths]
        )

        # Step 4: Final Synthesis - Select the best answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the refined reasoning chains:
            - Compare the validity and completeness of each chain.
            - Select the chain that provides the most accurate and concise answer.
            - Extract the precise answer span from the selected chain.""",
            contexts_list=refined_paths
        )

        # Step 5: Summarize the Answer
        concise_answer = await self.summarize(
            instruction="Condense the final answer into a short, factual response.",
            context=final_answer
        )

        return concise_answer