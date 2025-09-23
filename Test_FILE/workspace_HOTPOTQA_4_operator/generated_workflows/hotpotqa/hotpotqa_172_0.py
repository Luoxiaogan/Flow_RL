# Workflow ID: hotpotqa_172_0
# Benchmark: hotpotqa
# Data Indices: [249, 266]

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
            instruction="""Analyze the question and classify it into one of the following types:
            - Bridge Question: Requires connecting entities across documents.
            - Comparison Question: Involves comparing properties or facts.
            - Compositional Question: Combines multiple facts to derive an answer.
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entities_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from the following document:
                {doc}
                Format as a structured list with categories: People, Places, Numbers, Actions.""",
                context=""
            )
            for doc in ["Document 1", "Document 2", "Document 3"]  # Dynamically adjust based on input
        ]
        entities_results = await asyncio.gather(*entities_tasks)

        # Step 3: Refine extracted entities and relationships
        refined_entities = await asyncio.gather(
            *[self.revise(
                instruction="Ensure completeness and accuracy of extracted entities and relationships.",
                context=result
            ) for result in entities_results]
        )

        # Step 4: Build the reasoning chain
        reasoning_chain = ""
        for i in range(len(refined_entities) - 1):
            connection = await self.generate(
                instruction=f"""Connect the following sets of entities:
                Set 1: {refined_entities[i]}
                Set 2: {refined_entities[i + 1]}
                Identify shared entities or relationships and explain the logical connection.""",
                context=reasoning_chain
            )
            reasoning_chain += connection

        # Step 5: Extract the answer
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction="Extract the precise answer from the reasoning chain.",
                context=reasoning_chain
            ),
            self.generate(
                instruction="Cross-check the answer with supporting facts from the documents.",
                context=reasoning_chain
            )
        )

        # Step 6: Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and factually correct answer.",
            contexts_list=candidate_answers
        )

        return final_answer