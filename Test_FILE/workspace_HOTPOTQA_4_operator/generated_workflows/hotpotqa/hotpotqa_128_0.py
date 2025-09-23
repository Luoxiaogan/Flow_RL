# Workflow ID: hotpotqa_128_0
# Benchmark: hotpotqa
# Data Indices: [153, 34]

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

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. What entities are mentioned in the question?
            3. What is the expected answer format?
            Provide structured classification.""",
            context=""
        )

        # Phase 2: Entity and Relationship Extraction
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from Document {i+1}:
                - Identify people, places, organizations, and other key entities
                - Note their relationships and roles
                - Format as structured list""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        summarized_entities = await asyncio.gather(
            *[self.summarize(
                instruction="Condense extracted entities into concise format",
                context=entities
            ) for entities in extracted_entities]
        )

        # Phase 3: Building Reasoning Chains
        bridge_entity_identification = await self.generate(
            instruction=f"""Identify bridge entities that connect multiple documents:
            Extracted Entities: {summarized_entities}
            Question Analysis: {analysis}
            Find entities that appear in multiple documents and are relevant to the question.""",
            context=""
        )

        reasoning_chain = await self.generate(
            instruction=f"""Build reasoning chain using bridge entities:
            Bridge Entities: {bridge_entity_identification}
            Summarized Entities: {summarized_entities}
            Follow connections between documents to derive the answer.""",
            context=""
        )

        refined_reasoning_chain = await self.revise(
            instruction="Refine reasoning chain to ensure logical soundness and factual correctness",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract precise answer from final document:
            Refined Reasoning Chain: {refined_reasoning_chain}
            Extract exact answer span that directly answers the question.""",
            context=""
        )

        validation_tasks = [
            self.generate(
                instruction=f"""Validate answer against reasoning chain:
                Answer: {answer_extraction}
                Reasoning Chain: {refined_reasoning_chain}
                Ensure the answer is factually correct and supported by the chain.""",
                context=""
            ) for _ in range(3)  # Multiple validations for robustness
        ]
        validations = await asyncio.gather(*validation_tasks)

        final_answer = await self.ensemble(
            instruction="Select the most valid and supported answer",
            contexts_list=validations
        )

        return final_answer