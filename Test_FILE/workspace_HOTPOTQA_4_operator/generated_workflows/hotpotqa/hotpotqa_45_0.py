# Workflow ID: hotpotqa_45_0
# Benchmark: hotpotqa
# Data Indices: [387]

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

        # Step 1: Initial Analysis - Classify question type and extract bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify candidate bridge entities (shared entities across documents).
            3. List all relevant documents and their key facts.
            Provide structured output.""",
            context=""
        )

        # Step 2: Entity Exploration - Explore bridge entities in parallel
        entities = [entity.strip() for entity in initial_analysis.split("\n") if "Entity:" in entity]
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""For the bridge entity '{entity}':
                1. Identify all documents mentioning this entity.
                2. Build a reasoning chain connecting these documents.
                3. Extract supporting facts for each step in the chain.
                Provide structured output.""",
                context=initial_analysis
            ) for entity in entities]
        )

        # Step 3: Reasoning Chain Refinement - Validate and refine each chain
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the reasoning chain for '{entity}':
                1. Ensure logical consistency.
                2. Add missing details.
                3. Validate supporting facts.
                Provide improved reasoning chain.""",
                context=chain
            ) for entity, chain in zip(entities, reasoning_chains)]
        )

        # Step 4: Ensemble Selection - Choose the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Compare reasoning chains:
            1. Evaluate completeness and logical consistency.
            2. Select the most robust chain with strongest supporting facts.
            Provide the selected chain.""",
            contexts_list=refined_chains
        )

        # Step 5: Answer Extraction - Extract the final answer
        final_answer = await self.generate(
            instruction=f"""Using the selected reasoning chain:
            {best_chain}
            
            Extract the final answer:
            1. Ensure it is a precise text span or yes/no response.
            2. Validate against supporting facts.
            Provide the final answer.""",
            context=best_chain
        )

        # Step 6: Validation and Feedback - Validate the final answer
        validation = await self.revise(
            instruction=f"""Validate the final answer:
            {final_answer}
            
            1. Check factual correctness.
            2. Ensure alignment with supporting facts.
            Provide validation feedback.""",
            context=final_answer
        )

        # Return the final answer if validated, otherwise indicate failure
        if "error" not in validation.lower():
            return final_answer
        else:
            return "Validation failed. Please review the reasoning chain."