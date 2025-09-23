# Workflow ID: hotpotqa_87_0
# Benchmark: hotpotqa
# Data Indices: [255, 411]

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

        # Step 1: Classify the question type and identify key components
        question_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify key entities and relationships mentioned in the question.
            - Provide a structured breakdown of the problem.""",
            context=""
        )

        # Step 2: Extract relevant entities and relationships from documents
        entity_extraction = await self.generate(
            instruction=f"""Extract relevant entities and relationships from the context documents:
            Question Analysis: {question_analysis}
            Focus on entities and relationships that align with the question type.
            Format as a structured list with categories:
            - Bridge Entities: [entities connecting documents]
            - Supporting Facts: [facts related to the question]""",
            context=question_analysis
        )

        # Step 3: Generate reasoning chains for each bridge entity (Parallel Fork)
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain for the following bridge entity:
                Entity: {entity}
                Use the context documents to connect the entity to the final answer.
                Ensure logical consistency and document coverage.""",
                context=entity_extraction
            ) for entity in entity_extraction.split("\n") if "Bridge Entities" in entity]
        )

        # Step 4: Select the most plausible reasoning chain (Ensemble)
        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most plausible one:
            Criteria:
            - Logical consistency across documents
            - Coverage of supporting facts
            - Alignment with the question type""",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract and refine the final answer (Iterative Loop)
        refined_answer = best_chain
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain and extract the final answer:
                Reasoning Chain: {refined_answer}
                Ensure the answer is factually correct and supported by the documents.
                Extract the exact answer span from the relevant document.""",
                context=refined_answer
            )
            refined_answer = await self.revise(
                instruction=f"""Refine the extracted answer based on validation feedback:
                Validation: {validation}
                Ensure precision and factual accuracy.""",
                context=refined_answer
            )
            if "error" not in validation.lower():
                break

        return refined_answer