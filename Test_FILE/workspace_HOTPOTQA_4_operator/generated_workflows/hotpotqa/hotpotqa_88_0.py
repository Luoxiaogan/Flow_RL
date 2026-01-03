# Workflow ID: hotpotqa_88_0
# Benchmark: hotpotqa
# Data Indices: [216, 76]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            1. Is this a bridge, comparison, or compositional question?
            2. Identify all named entities, relationships, and constraints.
            3. Highlight potential bridge entities for bridge questions.
            4. For comparison questions, identify the properties to compare.
            Provide structured output.""",
            context=""
        )

        # Step 2: Conditional Branching Based on Question Type
        if "bridge" in initial_analysis.lower():
            # Parallel exploration of reasoning chains
            bridge_entities = await self.generate(
                instruction=f"""Extract all potential bridge entities and their connections:
                {initial_analysis}
                
                List all entities that connect documents and their roles.""",
                context=initial_analysis
            )
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Trace reasoning chain starting from {entity}:
                    - Identify connected documents
                    - Extract relevant facts
                    - Build logical sequence""",
                    context=initial_analysis
                ) for entity in bridge_entities.split('\n')]
            )
        elif "comparison" in initial_analysis.lower():
            # Parallel extraction of properties
            properties = await self.generate(
                instruction=f"""Extract properties to compare:
                {initial_analysis}
                
                List properties and their values from each document.""",
                context=initial_analysis
            )
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Analyze property {prop}:
                    - Compare values across documents
                    - Determine which is greater/smaller/earlier/later""",
                    context=initial_analysis
                ) for prop in properties.split('\n')]
            )
        else:  # Compositional questions
            # Sequential composition of facts
            reasoning_chains = []
            facts = await self.generate(
                instruction=f"""Extract all relevant facts:
                {initial_analysis}
                
                List facts in logical order.""",
                context=initial_analysis
            )
            for fact in facts.split('\n'):
                reasoning_chains.append(await self.generate(
                    instruction=f"""Integrate fact {fact} into reasoning chain:
                    - Connect to previous facts
                    - Maintain logical consistency""",
                    context="\n".join(reasoning_chains)
                ))

        # Step 3: Validation and Refinement
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Verify factual correctness and logical consistency.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 4: Synthesis
        final_answer = await self.ensemble(
            instruction="Combine reasoning chains into final answer. Ensure precision and factual correctness.",
            contexts_list=refined_chains
        )

        # Step 5: Iterative Refinement (Optional)
        for _ in range(2):  # Allow up to 2 iterations
            validation = await self.generate(
                instruction="Validate final answer against original question and documents.",
                context=final_answer
            )
            if "error" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=final_answer
                )
            else:
                break

        return final_answer