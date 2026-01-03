# Workflow ID: hotpotqa_46_0
# Benchmark: hotpotqa
# Data Indices: [318]

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
            - Bridge: Requires connecting entities across documents.
            - Comparison: Involves comparing attributes across documents.
            - Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract named entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities and relationships from the documents:
            - People: Names and roles
            - Places: Locations and contexts
            - Numbers: Values and what they represent
            - Actions: What happens and when
            Format as structured lists. Question Type: {question_type}""",
            context=""
        )

        # Step 3: Identify bridge entities or comparable attributes
        bridge_entities = await self.generate(
            instruction=f"""Identify bridge entities or comparable attributes based on the question type:
            - Bridge: Find shared entities across documents.
            - Comparison: Identify attributes to compare.
            - Compositional: Extract relevant facts.
            Entities: {entities}""",
            context=entities
        )

        # Step 4: Construct reasoning chains in parallel
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct reasoning chain 1:
                - Start with primary document.
                - Follow logical connections to other documents.
                Entities: {bridge_entities}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct reasoning chain 2:
                - Explore alternative connections.
                - Validate against extracted entities.
                Entities: {bridge_entities}""",
                context=entities
            )
        )

        # Step 5: Refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity and logical consistency.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 6: Synthesize the best reasoning chain
        best_chain = await self.ensemble(
            instruction="Select the most robust reasoning chain based on completeness and coherence.",
            contexts_list=refined_chains
        )

        # Step 7: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            - Ensure factual correctness.
            - Match exact answer spans.
            Best Chain: {best_chain}""",
            context=best_chain
        )

        return answer