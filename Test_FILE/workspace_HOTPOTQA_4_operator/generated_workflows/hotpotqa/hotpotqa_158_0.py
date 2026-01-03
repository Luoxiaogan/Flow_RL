# Workflow ID: hotpotqa_158_0
# Benchmark: hotpotqa
# Data Indices: [358]

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

        # Step 1: Question Classification
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting entities across documents (e.g., "What nationality is the director of [movie]?")
            2. Comparison Question: Involves comparing properties across documents (e.g., "Which was founded first, X or Y?")
            3. Compositional Question: Combines multiple facts to derive an answer
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Entity Extraction
        entities = await self.generate(
            instruction=f"""Extract all key entities, relationships, and numerical values from the documents. 
            Format as a structured list:
            - Entities: [names, titles, concepts]
            - Relationships: [connections between entities]
            - Numerical Values: [dates, quantities, etc.]""",
            context=""
        )

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify entities that connect multiple documents. 
            Evaluate overlaps and select the most plausible bridge entities.""",
            contexts_list=[entities, question_type]
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain to answer the question:
            - Start from the question and follow the bridge entities
            - Link facts across documents step-by-step
            - Ensure each link is factually correct and supported by the documents
            Bridge Entities: {bridge_entities}""",
            context=entities
        )

        # Step 5: Answer Extraction and Validation
        raw_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is a short factual span
            - Verify it matches the expected format (yes/no, entity/phrase)
            Reasoning Chain: {reasoning_chain}""",
            context=reasoning_chain
        )

        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Check if it is factually correct based on the documents
            - Ensure it is supported by the reasoning chain
            - Resolve any ambiguities or conflicts
            Raw Answer: {raw_answer}""",
            context=reasoning_chain
        )

        return validated_answer