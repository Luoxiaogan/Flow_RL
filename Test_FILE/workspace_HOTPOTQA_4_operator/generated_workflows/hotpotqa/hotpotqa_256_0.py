# Workflow ID: hotpotqa_256_0
# Benchmark: hotpotqa
# Data Indices: [264]

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
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities and relationships:
            - Identify keywords indicating the question type
            - Extract named entities (people, organizations, dates, etc.)
            - Identify relationships between entities
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Extract entities from all documents in parallel
        documents = re.findall(r"Document \d+:.*?(?=\n\nDocument|\Z)", self.problem_text, re.DOTALL)
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities and relationships from the following document:
                {doc}
                Focus on entities and relationships relevant to the question type: {classification}""",
                context=""
            ) for doc in documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Refine entities to ensure relevance
        refined_entities = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the entities to retain only those relevant to the question:
                Question: {classification}
                Entities: {entities}""",
                context=entities
            ) for entities in extracted_entities]
        )

        # Step 4: Build reasoning chain iteratively
        reasoning_chain = ""
        for i, entities in enumerate(refined_entities):
            step = await self.generate(
                instruction=f"""Using the refined entities from document {i+1}:
                {entities}
                Build the next step in the reasoning chain based on the question type: {classification}
                Ensure coherence with previous steps: {reasoning_chain}""",
                context=reasoning_chain
            )
            reasoning_chain += f"\nStep {i+1}: {step}"

        # Step 5: Extract and validate the answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short, factual span directly from the text.""",
            context=reasoning_chain
        )

        # Step 6: Validate the answer against supporting facts
        validation = await self.generate(
            instruction=f"""Validate the extracted answer:
            Answer: {answer}
            Supporting Facts: {reasoning_chain}
            Ensure the answer is factually correct and supported by the reasoning chain.""",
            context=reasoning_chain
        )

        # Return the final answer
        return answer