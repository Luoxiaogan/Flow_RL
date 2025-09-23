# Workflow ID: hotpotqa_196_0
# Benchmark: hotpotqa
# Data Indices: [453]

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
            - Bridge: Requires connecting shared entities across documents.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities, numbers, and relationships from Document {i+1}:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )
            for i in range(10)  # Assuming up to 10 documents
        ]
        entities_list = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Construct reasoning chain based on question type
        reasoning_chain = await self.ensemble(
            instruction=f"""Given the question type ({question_type}) and extracted entities:
            - Build a reasoning chain that connects the entities across documents.
            - For bridge questions, find shared entities.
            - For comparison questions, align comparable properties.
            - For compositional questions, chain multiple facts.
            Provide a detailed reasoning chain.""",
            contexts_list=entities_list
        )

        # Step 4: Extract precise answer span
        answer_span = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the final document.
            - Ensure the answer is factually correct.
            - Include supporting facts from different documents.
            Provide the exact answer span.""",
            context=""
        )

        # Step 5: Validate and refine the answer
        refined_answer = await self.revise(
            instruction="""Verify the answer:
            - Check factual correctness.
            - Ensure the answer matches the question type.
            - Improve clarity and precision if needed.""",
            context=answer_span
        )

        return refined_answer