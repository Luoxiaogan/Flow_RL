# Workflow ID: hotpotqa_155_0
# Benchmark: hotpotqa
# Data Indices: [26]

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
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (comparing properties across documents)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities, relationships, and key facts from Document {i+1}.
                Focus on entities that could connect to other documents or answer the question.
                Format as structured list with categories:
                - Entities: [names and roles]
                - Relationships: [connections between entities]
                - Key Facts: [important information]""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        entities_list = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Synthesize information from the extracted entities to build a reasoning chain:
            - Identify shared entities across documents
            - Connect facts to form a logical chain leading to the answer
            Question Type: {classification}""",
            contexts_list=entities_list
        )

        # Step 4: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Using the reasoning chain: {reasoning_chain}
            Extract the precise answer from the relevant document(s).
            Ensure the answer is factually correct and supported by evidence.
            Format as short text span or yes/no response.""",
            context=""
        )

        # Step 5: Refine and validate the answer
        refined_answer = await self.revise(
            instruction=f"""Validate and refine the extracted answer:
            - Ensure factual correctness
            - Verify supporting facts from the reasoning chain
            - Adjust phrasing for clarity and precision""",
            context=answer
        )

        return refined_answer