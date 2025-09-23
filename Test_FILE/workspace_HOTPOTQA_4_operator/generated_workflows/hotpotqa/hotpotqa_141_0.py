# Workflow ID: hotpotqa_141_0
# Benchmark: hotpotqa
# Data Indices: [96]

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
        classification = await self.generate(
            instruction="""Classify the question type:
            - Bridge: Connects entities across documents (e.g., "What nationality is the director of [movie]?")
            - Comparison: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional: Combines multiple facts to derive an answer
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract key entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities and relationships from the question:
            Classification: {classification}
            Format as structured list:
            - Entities: [names and roles]
            - Relationships: [what connects them]""",
            context=classification
        )

        # Step 3: Parallel document search for each entity
        search_tasks = []
        for entity in entities.split("\n"):
            if entity.strip():
                search_tasks.append(
                    self.generate(
                        instruction=f"""Search all documents for information about:
                        Entity: {entity}
                        Return relevant sentences or paragraphs.""",
                        context=""
                    )
                )
        search_results = await asyncio.gather(*search_tasks)

        # Step 4: Synthesize results from parallel searches
        synthesized_results = await self.ensemble(
            instruction="Synthesize results from parallel searches, prioritizing relevance.",
            contexts_list=search_results
        )

        # Step 5: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain:
            Search Results: {synthesized_results}
            Connect entities across documents and document the reasoning chain.
            Cite specific sentences and documents.""",
            context=synthesized_results
        )

        # Step 6: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is factual, supported by evidence, and matches the expected format.""",
            context=reasoning_chain
        )

        validated_answer = await self.revise(
            instruction=f"""Validate the answer:
            Answer: {answer}
            Ensure it aligns with the question and supporting facts.
            Correct any errors or ambiguities.""",
            context=answer
        )

        return validated_answer