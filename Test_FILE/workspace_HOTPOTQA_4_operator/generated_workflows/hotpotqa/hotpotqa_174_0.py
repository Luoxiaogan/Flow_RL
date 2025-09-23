# Workflow ID: hotpotqa_174_0
# Benchmark: hotpotqa
# Data Indices: [106, 40]

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
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities, numbers, and relationships.
            3. Identify potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Bridge Entity Identification - Validate and rank potential bridge entities
        bridge_entities = await self.revise(
            instruction=f"""Validate and rank potential bridge entities:
            - Evaluate relevance to the question.
            - Check for connections across documents.
            - Rank entities by confidence score.
            Input: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration - Explore connections for top bridge entities
        top_entities = [entity.strip() for entity in bridge_entities.split("\n") if entity.strip()]
        explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Explore connections for bridge entity: {entity}
                - Find supporting facts in different documents.
                - Build reasoning chains linking documents.
                - Identify potential answers.""",
                context=initial_analysis
            ) for entity in top_entities[:3]]  # Limit to top 3 entities for efficiency
        )

        # Step 4: Synthesis and Validation - Select best-supported answer
        synthesis = await self.ensemble(
            instruction="""Synthesize results from parallel explorations:
            - Select the most coherent and well-supported answer.
            - Ensure the reasoning chain is complete and factual.
            - Validate against the original question.""",
            contexts_list=explorations
        )

        # Step 5: Final Answer Extraction - Extract precise answer span
        final_answer = await self.generate(
            instruction=f"""Extract the precise answer span from the synthesis:
            - Ensure the answer is factually correct.
            - Match the required format (short text span or yes/no).
            Synthesis: {synthesis}""",
            context=synthesis
        )

        return final_answer