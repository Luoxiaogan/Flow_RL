# Workflow ID: hotpotqa_281_0
# Benchmark: hotpotqa
# Data Indices: [414]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the question:
            1. Identify key entities (people, places, concepts).
            2. Classify the question type (bridge, comparison, compositional).
            3. Extract constraints and requirements.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Entity Linking and Document Matching
        entities = await self.generate(
            instruction=f"""From the analysis: {analysis}
            Extract all entities and match them to relevant documents.
            Focus on entities that connect multiple documents.
            Provide a mapping of entities to documents.""",
            context=analysis
        )
        matched_docs = await asyncio.gather(
            *[self.generate(
                instruction=f"Find sentences mentioning {entity} in the documents.",
                context=entities
            ) for entity in entities.split("\n") if entity.strip()]
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the matched sentences for {entity}, construct a reasoning chain.
                Connect the sentences logically to answer the question.""",
                context="\n".join(matched_docs)
            ) for entity in entities.split("\n") if entity.strip()]
        )
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain.",
            contexts_list=reasoning_chains
        )

        # Phase 4: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {best_chain}
            Ensure the answer is a short, factual span directly from the text.""",
            context=best_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the answer against the original question and documents.",
            context=answer
        )

        # Phase 5: Iterative Refinement (Optional)
        for _ in range(2):  # Allow up to 2 refinements
            validation = await self.generate(
                instruction="Check if the answer is complete and accurate.",
                context=validated_answer
            )
            if "error" in validation.lower():
                validated_answer = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=validated_answer
                )
            else:
                break

        return validated_answer