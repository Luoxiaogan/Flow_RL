# Workflow ID: hotpotqa_48_0
# Benchmark: hotpotqa
# Data Indices: [422]

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
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (evaluating properties)?
            3. Is it a compositional question (combining facts)?
            Provide a structured classification with reasoning.""",
            context=""
        )

        # Step 2: Extract named entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities and relationships from the documents:
            - Identify people, places, organizations, and key concepts.
            - Highlight entities mentioned in both the question and documents.
            - Format as structured list with categories.
            Question Type: {question_type}""",
            context=""
        )

        # Step 3: Generate reasoning chains in parallel
        candidate_entities = [e.strip() for e in entities.split("\n") if e.strip()]
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Build a reasoning chain for entity: {entity}
                - Connect the entity to the question's goal.
                - Extract relevant facts from the documents.
                - Ensure logical consistency.""",
                context=entities
            ) for entity in candidate_entities]
        )

        # Step 4: Validate and refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this reasoning chain:
                - Check logical consistency.
                - Verify factual accuracy.
                - Address any inconsistencies.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Synthesize the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Select the most consistent and accurate reasoning chain:
            - Prioritize chains with clear evidence from multiple documents.
            - Ensure the chain leads to a precise answer span.""",
            contexts_list=refined_chains
        )

        # Step 6: Extract the final answer
        final_answer = await self.generate(
            instruction=f"""Extract the exact answer span from the reasoning chain:
            - Ensure the answer is factually correct.
            - Directly address the question.
            Best Chain: {best_chain}""",
            context=best_chain
        )

        return final_answer