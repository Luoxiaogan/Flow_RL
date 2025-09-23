# Workflow ID: hotpotqa_26_0
# Benchmark: hotpotqa
# Data Indices: [163]

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
            instruction="""Classify the question into one of the following categories:
            1. Bridge Question: Requires connecting documents through shared entities.
            2. Comparison Question: Involves comparing properties across documents.
            3. Compositional Question: Combines multiple facts to derive the answer.
            Provide the category and a brief explanation.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the documents:
            - Entities: Names, places, organizations, etc.
            - Numbers: Dates, quantities, etc.
            - Relationships: Connections between entities.
            Format as structured lists.
            Question Type: {classification}""",
            context=""
        )

        # Step 3: Construct reasoning chains (parallel exploration)
        if "Bridge" in classification:
            chains = await asyncio.gather(
                self.generate(
                    instruction=f"""Identify shared entities between documents and construct reasoning chains.
                    Entities: {entities}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Explore alternative reasoning chains in case primary ones fail.
                    Entities: {entities}""",
                    context=""
                )
            )
        elif "Comparison" in classification:
            chains = await asyncio.gather(
                self.generate(
                    instruction=f"""Compare attributes across documents.
                    Attributes: {entities}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Validate comparisons by cross-referencing additional documents.
                    Attributes: {entities}""",
                    context=""
                )
            )
        else:  # Compositional
            chains = await asyncio.gather(
                self.generate(
                    instruction=f"""Combine facts iteratively to derive the answer.
                    Facts: {entities}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Explore alternative combinations in case primary ones fail.
                    Facts: {entities}""",
                    context=""
                )
            )

        # Step 4: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain based on evidence.",
            contexts_list=chains
        )

        # Step 5: Validate and refine the reasoning chain
        refined_chain = await self.revise(
            instruction="Critique and improve the reasoning chain for accuracy and completeness.",
            context=best_chain
        )

        # Step 6: Extract and summarize the final answer
        answer = await self.summarize(
            instruction="Extract the precise answer from the refined reasoning chain.",
            context=refined_chain
        )

        return answer