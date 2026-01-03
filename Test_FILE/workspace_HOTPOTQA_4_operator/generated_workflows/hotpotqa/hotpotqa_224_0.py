# Workflow ID: hotpotqa_224_0
# Benchmark: hotpotqa
# Data Indices: [259, 17]

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

        # Step 1: Analyze the question and classify its type
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting entities across documents.
            2. Comparison Question: Involves comparing properties across documents.
            3. Compositional Question: Combines multiple facts to derive the answer.
            Provide structured output including:
            - Question Type
            - Key Entities
            - Expected Answer Format""",
            context=""
        )

        # Step 2: Identify entities and map them to documents
        entities = await self.generate(
            instruction=f"""Extract all named entities from the question:
            {classification}
            Then, locate these entities in the provided context documents.
            Return a mapping of entities to document titles.""",
            context=""
        )

        # Step 3: Construct reasoning chain (parallel processing)
        reasoning_tasks = []
        for entity in entities.split("\n"):
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""For the entity '{entity}', extract relevant sentences 
                    from its corresponding document and identify connections to other entities.""",
                    context=entities
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Step 4: Synthesize reasoning chains and extract answer
        synthesized_chain = await self.ensemble(
            instruction="Combine the reasoning chains into a coherent narrative.",
            contexts_list=reasoning_chains
        )

        answer_extraction = await self.summarize(
            instruction=f"""From the synthesized reasoning chain:
            {synthesized_chain}
            Extract the precise answer span that directly answers the question.""",
            context=synthesized_chain
        )

        # Step 5: Validate and refine the answer
        validated_answer = await self.revise(
            instruction=f"""Verify the extracted answer:
            {answer_extraction}
            Ensure it is factually correct and matches the reasoning chain.
            Refine if necessary.""",
            context=answer_extraction
        )

        return validated_answer