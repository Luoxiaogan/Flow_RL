# Workflow ID: hotpotqa_205_0
# Benchmark: hotpotqa
# Data Indices: [327]

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

        # Step 1: Classify the question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type and extract key entities:
            1. Is it a bridge, comparison, or compositional question?
            2. Identify all named entities, relationships, and constraints.
            Provide structured output with categories:
            - Question Type: [bridge/comparison/compositional]
            - Entities: [list of entities]
            - Relationships: [list of relationships]""",
            context=""
        )

        # Parse classification results
        question_type = "bridge" if "bridge" in classification.lower() else "comparison" if "comparison" in classification.lower() else "compositional"
        entities = await self.generate(
            instruction="Extract all named entities and their roles from the context documents.",
            context=classification
        )

        # Step 2: Explore reasoning chains in parallel
        if question_type == "bridge":
            reasoning_chains = await asyncio.gather(
                self.generate(
                    instruction=f"""Find shared entities between documents that connect the question to the answer.
                    Entities: {entities}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Propose alternative reasoning chains based on secondary entities.
                    Entities: {entities}""",
                    context=""
                )
            )
        elif question_type == "comparison":
            reasoning_chains = await asyncio.gather(
                self.generate(
                    instruction=f"""Compare properties across documents to answer the question.
                    Entities: {entities}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Identify contrasting facts that support the comparison.
                    Entities: {entities}""",
                    context=""
                )
            )
        else:  # Compositional
            reasoning_chains = await asyncio.gather(
                self.generate(
                    instruction=f"""Combine multiple facts to derive the answer.
                    Entities: {entities}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Explore alternative combinations of facts.
                    Entities: {entities}""",
                    context=""
                )
            )

        # Step 3: Refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity and logical consistency of the reasoning chain.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 4: Synthesize the best reasoning chain
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain based on supporting evidence and logical consistency.",
            contexts_list=refined_chains
        )

        # Step 5: Extract the precise answer
        answer = await self.summarize(
            instruction="Extract the exact answer span from the reasoning chain. Ensure precision and adherence to the expected format.",
            context=best_chain
        )

        return answer