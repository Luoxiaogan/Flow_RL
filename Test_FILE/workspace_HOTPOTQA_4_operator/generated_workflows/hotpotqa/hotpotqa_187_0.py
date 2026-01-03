# Workflow ID: hotpotqa_187_0
# Benchmark: hotpotqa
# Data Indices: [444]

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
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts to derive the answer.
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and key facts from the documents.
            Focus on entities that could serve as bridge entities.
            Question Type: {question_type}""",
            context=""
        )

        # Step 3: Build reasoning chains in parallel
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain using the following entities:
                {entities}
                Ensure the chain connects the question to a potential answer.
                Question Type: {question_type}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct an alternative reasoning chain using the following entities:
                {entities}
                Explore a different connection or perspective.
                Question Type: {question_type}""",
                context=entities
            )
        )

        # Step 4: Refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Refine the reasoning chain for clarity, accuracy, and completeness.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="Select the most robust and accurate reasoning chain.",
            contexts_list=refined_chains
        )

        # Step 6: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the final document in the reasoning chain.
            Validate the answer against supporting facts.
            Reasoning Chain: {best_chain}""",
            context=best_chain
        )

        # Step 7: Handle ambiguity or failure
        if "unclear" in answer.lower() or "ambiguous" in answer.lower():
            fallback_answer = await self.generate(
                instruction="Attempt a heuristic-based approach to extract the answer.",
                context=best_chain
            )
            return fallback_answer

        return answer