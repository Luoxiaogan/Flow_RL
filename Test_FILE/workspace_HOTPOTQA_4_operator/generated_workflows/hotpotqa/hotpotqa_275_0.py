# Workflow ID: hotpotqa_275_0
# Benchmark: hotpotqa
# Data Indices: [362]

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
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Based on the question type ({question_type}), extract:
            - Key entities (people, places, organizations)
            - Relationships between entities
            - Relevant properties or attributes
            Format as structured list.""",
            context=question_type
        )

        # Step 3: Generate reasoning chains in parallel
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Generate a reasoning chain connecting the following entities:
                {entities}
                Ensure logical coherence and factual correctness.""",
                context=""
            ) for _ in range(3)]  # Generate 3 chains
        )

        # Step 4: Validate and select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Evaluate reasoning chains based on:
            - Factual correctness
            - Logical coherence
            - Alignment with the question
            Select the most promising chain.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {best_chain}
            Ensure the answer is supported by explicit evidence.""",
            context=best_chain
        )

        # Step 6: Iterative refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the answer:
            {answer}
            Check for factual correctness and completeness.""",
            context=answer
        )
        if "error" in validation.lower() or "incomplete" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                {validation}""",
                context=answer
            )
            return refined_answer

        return answer