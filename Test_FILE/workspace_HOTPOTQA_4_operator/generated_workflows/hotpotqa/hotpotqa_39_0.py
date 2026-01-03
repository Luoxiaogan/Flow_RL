# Workflow ID: hotpotqa_39_0
# Benchmark: hotpotqa
# Data Indices: [395]

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
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting entities across documents
            - Comparison: Involves comparing attributes
            - Compositional: Combines multiple facts
            Then extract all named entities (people, places, dates, etc.) and their relationships.
            Format the output as:
            Question Type: [type]
            Entities: [list of entities and relationships]""",
            context=""
        )

        # Parse classification results
        question_type = "Bridge" if "Bridge" in classification else "Comparison" if "Comparison" in classification else "Compositional"
        entities = classification.split("Entities:")[1].strip()

        # Step 2: Parallel exploration of reasoning chains
        reasoning_tasks = []
        if question_type == "Bridge":
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Find the bridge entity that connects the documents based on:
                    {entities}
                    Identify the document and sentence containing the bridge entity.""",
                    context=entities
                )
            )
        elif question_type == "Comparison":
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Extract comparable attributes from the documents based on:
                    {entities}
                    Focus on temporal or ordinal data.""",
                    context=entities
                )
            )
        else:  # Compositional
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Chain the relationships between entities based on:
                    {entities}
                    Derive the final fact required to answer the question.""",
                    context=entities
                )
            )

        reasoning_results = await asyncio.gather(*reasoning_tasks)

        # Step 3: Summarize and refine reasoning chains
        refined_reasoning = await asyncio.gather(
            *[self.revise(
                instruction="Refine the reasoning chain to ensure logical consistency and factual accuracy.",
                context=result
            ) for result in reasoning_results]
        )

        # Step 4: Ensemble selection of the best reasoning chain
        final_reasoning = await self.ensemble(
            instruction="Select the most accurate and complete reasoning chain.",
            contexts_list=refined_reasoning
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Based on the final reasoning chain:
            {final_reasoning}
            Extract the exact answer span from the relevant document. Ensure it is factually correct and concise.""",
            context=final_reasoning
        )

        return answer