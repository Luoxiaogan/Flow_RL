# Workflow ID: hotpotqa_303_0
# Benchmark: hotpotqa
# Data Indices: [474]

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
            instruction="""Classify the question into one of three types:
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts to derive an answer.
            Provide a structured classification with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and identify bridge entities
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from Document {i}.
                Format as a structured list with categories: People, Places, Numbers, Actions.""",
                context=""
            ) for i in range(1, 11)  # Assuming up to 10 documents
        ]
        entity_lists = await asyncio.gather(*entity_extraction_tasks)

        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities that connect documents.
            A bridge entity is a shared concept, person, or place that links two or more documents.
            Select the most relevant bridge entities based on the question type.""",
            contexts_list=entity_lists
        )

        # Step 3: Construct the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entities: {bridge_entities}
            Construct a reasoning chain that connects the documents logically.
            Follow the chain step-by-step to arrive at the answer.""",
            context=classification
        )

        refined_chain = await self.revise(
            instruction="""Review the reasoning chain for logical consistency.
            Fix any gaps or errors in the chain. Ensure it leads to a valid conclusion.""",
            context=reasoning_chain
        )

        # Step 4: Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain: {refined_chain}
            Ensure the answer is factually correct and matches the expected format (short text span or yes/no).""",
            context=""
        )

        supporting_facts = await self.summarize(
            instruction="""Condense the supporting facts from the reasoning chain.
            Include only the facts that directly support the answer.""",
            context=refined_chain
        )

        validated_answer = await self.ensemble(
            instruction="""Validate the answer against the supporting facts.
            Ensure the answer is fully supported and free of contradictions.""",
            contexts_list=[answer_extraction, supporting_facts]
        )

        return validated_answer