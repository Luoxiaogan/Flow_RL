# Workflow ID: hotpotqa_203_0
# Benchmark: hotpotqa
# Data Indices: [205]

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

        # Phase 1: Problem Analysis and Entity Extraction
        entities = await self.generate(
            instruction="""Extract all key entities and relationships from the question:
            - Identify named entities (people, organizations, locations)
            - Highlight relationships between entities
            - Note any constraints or conditions
            Format as a structured list.""",
            context=""
        )

        # Phase 2: Bridge Entity Identification
        bridge_candidates = await self.generate(
            instruction=f"""Identify potential bridge entities that connect the documents:
            - Use the extracted entities: {entities}
            - Find entities mentioned in multiple documents
            - Prioritize entities relevant to the question
            List candidates with justifications.""",
            context=entities
        )

        # Ensemble to select the most plausible bridge entity
        bridge_entity = await self.ensemble(
            instruction="Select the best bridge entity based on relevance and coherence.",
            contexts_list=[bridge_candidates]
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using bridge entity: {entity}
                - Link documents through shared entities
                - Ensure logical coherence
                - Highlight supporting facts""",
                context=entities
            ) for entity in bridge_entity.split("\n") if entity.strip()]
        )

        # Ensemble to select the most coherent reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="Select the most coherent and complete reasoning chain.",
            contexts_list=reasoning_paths
        )

        # Phase 4: Answer Extraction and Validation
        answer_span = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            - Locate the exact phrase in the text
            - Ensure it matches the question's requirements
            Reasoning chain: {reasoning_chain}""",
            context=reasoning_chain
        )

        # Validate and refine the answer
        validated_answer = await self.revise(
            instruction="Ensure the answer is factually correct and matches the question's requirements.",
            context=answer_span
        )

        return validated_answer