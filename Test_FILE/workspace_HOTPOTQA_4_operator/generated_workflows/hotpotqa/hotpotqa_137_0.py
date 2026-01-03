# Workflow ID: hotpotqa_137_0
# Benchmark: hotpotqa
# Data Indices: [464]

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

        # Step 1: Question Classification and Entity Extraction
        classification = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify explicit and implicit entities
            - Determine relationships between entities
            - Highlight potential bridge entities that connect documents""",
            context=""
        )

        # Step 2: Document Mapping
        document_mapping = await self.generate(
            instruction=f"""Map the extracted entities to relevant documents:
            - Entities: {classification}
            - Find documents containing information about these entities
            - Prioritize documents with strong contextual matches""",
            context=classification
        )

        # Step 3: Parallel Reasoning Chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using the following:
                - Entities: {classification}
                - Document mapping: {document_mapping}
                - Explore connections between documents and synthesize information""",
                context=document_mapping
            ) for _ in range(3)]  # Generate 3 parallel chains
        )

        # Step 4: Validation and Refinement
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the reasoning chain and refine the extracted answer:
                - Ensure factual correctness
                - Extract precise answer spans
                - Highlight supporting facts""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Ensemble Selection
        final_answer = await self.ensemble(
            instruction="""Select the best-supported answer from the refined chains:
            - Evaluate strength of supporting evidence
            - Prioritize chains with clear and coherent reasoning
            - Choose the most precise and factual answer""",
            contexts_list=refined_chains
        )

        return final_answer