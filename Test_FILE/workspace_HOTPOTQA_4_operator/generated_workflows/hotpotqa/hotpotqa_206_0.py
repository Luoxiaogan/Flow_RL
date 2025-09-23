# Workflow ID: hotpotqa_206_0
# Benchmark: hotpotqa
# Data Indices: [213]

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

        # Step 1: Question Analysis
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question (connecting entities)?
            - Is it a comparison question (comparing properties)?
            - Is it compositional (combining facts)?
            Provide a structured classification and identify key requirements.""",
            context=""
        )

        # Step 2: Entity Extraction
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract entities and relationships from Document {i+1}:
                - Named entities (people, places, organizations)
                - Numerical data
                - Implicit relationships
                Format as structured list.""",
                context=""
            ) for i in range(10)  # Assuming 10 documents for this example
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Bridge Entity Identification
        bridge_entity_identification = await self.generate(
            instruction=f"""Identify bridge entities that connect the documents:
            - Shared entities between documents
            - Relationships that link these entities
            Use the extracted entities:
            {extracted_entities}
            Provide a structured list of bridge entities.""",
            context=""
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain_construction = await self.generate(
            instruction=f"""Construct a reasoning chain across documents:
            - Start with bridge entities: {bridge_entity_identification}
            - Follow connections to build a logical path
            - Ensure each step is supported by document evidence
            Provide a detailed reasoning chain.""",
            context=bridge_entity_identification
        )

        # Step 5: Answer Extraction and Validation
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain:
                - Focus on factual correctness
                - Ensure the answer is directly supported by the documents
                Reasoning chain: {reasoning_chain_construction}""",
                context=reasoning_chain_construction
            ),
            self.generate(
                instruction=f"""Validate the extracted answer:
                - Check for consistency with the reasoning chain
                - Ensure precision and factual accuracy
                Reasoning chain: {reasoning_chain_construction}""",
                context=reasoning_chain_construction
            )
        )

        # Step 6: Ensemble Selection
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the candidates:
            - Prioritize answers with strongest evidence
            - Ensure factual correctness and precision""",
            contexts_list=answer_candidates
        )

        return final_answer