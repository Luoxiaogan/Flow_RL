# Workflow ID: hotpotqa_6_0
# Benchmark: hotpotqa
# Data Indices: [273]

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

        # Step 1: Initial Analysis - Classify question type and identify potential bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract potential bridge entities (e.g., names, places, concepts).
            3. Provide structured classification and list of entities.""",
            context=""
        )

        # Step 2: Bridge Entity Selection - Choose the most promising bridge entity
        bridge_candidates = await self.generate(
            instruction=f"""From the initial analysis:
            {initial_analysis}
            
            Generate multiple candidates for bridge entities by analyzing:
            - Document titles and their relevance to the question.
            - Frequency and prominence of entities in the text.
            Provide a ranked list of candidates.""",
            context=initial_analysis
        )
        bridge_entity = await self.ensemble(
            instruction="Select the most relevant bridge entity based on frequency, prominence, and connection to the question.",
            contexts_list=[bridge_candidates]
        )

        # Step 3: Reasoning Chain Construction - Trace connections across documents
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the bridge entity '{bridge_entity}', construct a reasoning chain:
                - Start from the first document mentioning the entity.
                - Trace connections to other documents.
                - Ensure logical consistency and factual accuracy.
                Provide the complete chain.""",
                context=bridge_entity
            ) for _ in range(3)]  # Explore up to 3 chains in parallel
        )
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Refine the reasoning chain for clarity, consistency, and accuracy.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 4: Answer Extraction - Extract precise answer spans
        summarized_answers = await asyncio.gather(
            *[self.summarize(
                instruction="Extract the precise answer span from the reasoning chain.",
                context=chain
            ) for chain in refined_chains]
        )
        final_answer = await self.ensemble(
            instruction="Select the best answer based on clarity, relevance, and support from the documents.",
            contexts_list=summarized_answers
        )

        # Step 5: Validation and Refinement - Ensure correctness
        validation = await self.generate(
            instruction=f"""Validate the final answer:
            {final_answer}
            
            Check:
            1. Does it directly answer the question?
            2. Is it supported by the documents?
            3. Are there any contradictions or ambiguities?""",
            context=final_answer
        )
        if "error" in validation.lower() or "contradiction" in validation.lower():
            final_answer = await self.revise(
                instruction=f"Fix issues identified during validation: {validation}",
                context=final_answer
            )

        return final_answer