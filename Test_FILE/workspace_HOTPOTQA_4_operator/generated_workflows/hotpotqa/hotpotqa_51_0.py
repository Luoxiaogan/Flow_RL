# Workflow ID: hotpotqa_51_0
# Benchmark: hotpotqa
# Data Indices: [427]

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

        # Step 1: Classify question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify named entities (people, places, organizations)
            - Highlight relationships between entities
            - Determine the expected answer format (short text span or yes/no)
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel entity and relationship extraction
        entities, relationships = await asyncio.gather(
            self.generate(
                instruction="Extract all named entities from the context documents.",
                context=classification
            ),
            self.generate(
                instruction="Identify relationships between entities across documents.",
                context=classification
            )
        )

        # Step 3: Build reasoning chains based on question type
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""For bridge questions, identify shared entities and construct reasoning chains:
                Entities: {entities}
                Relationships: {relationships}""",
                context=classification
            ),
            self.generate(
                instruction=f"""For comparison questions, extract relevant properties and evaluate them:
                Entities: {entities}
                Relationships: {relationships}""",
                context=classification
            ),
            self.generate(
                instruction=f"""For compositional questions, combine facts from multiple documents:
                Entities: {entities}
                Relationships: {relationships}""",
                context=classification
            )
        )

        # Step 4: Refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Refine reasoning chain for factual accuracy and logical coherence.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Synthesize insights into a concise answer
        answer = await self.ensemble(
            instruction="Synthesize refined reasoning chains into a concise, factually supported answer.",
            contexts_list=refined_chains
        )

        return answer