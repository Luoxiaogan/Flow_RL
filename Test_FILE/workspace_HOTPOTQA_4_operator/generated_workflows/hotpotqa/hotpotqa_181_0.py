# Workflow ID: hotpotqa_181_0
# Benchmark: hotpotqa
# Data Indices: [396, 207]

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

        # Step 1: Initial Analysis - Identify Question Type and Key Entities
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Extract all named entities, numbers, and relationships:
               - People: [names and roles]
               - Places: [locations and contexts]
               - Numbers: [values and what they represent]
               - Actions: [what happens and when]
            Provide structured classification and entity list.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate Reasoning Chains
        entities = await self.generate(
            instruction=f"Extract bridge entities connecting documents based on: {analysis}",
            context=analysis
        )
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"Build reasoning chain using entity: {entity}",
                context=entities
            ) for entity in entities.split("\n") if entity.strip()]
        )

        # Step 3: Validation and Refinement - Validate Each Chain
        validated_chains = []
        for chain in reasoning_chains:
            validation = await self.revise(
                instruction=f"Validate reasoning chain: {chain}. Ensure factual correctness and logical consistency.",
                context=chain
            )
            if "error" not in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"Refine reasoning chain: {validation}",
                    context=chain
                )
                validated_chains.append(refined_chain)

        # Step 4: Summarize Valid Chains
        summarized_chains = await asyncio.gather(
            *[self.summarize(
                instruction=f"Condense reasoning chain: {chain}",
                context=chain
            ) for chain in validated_chains]
        )

        # Step 5: Final Synthesis - Combine Chains into Final Answer
        final_answer = await self.ensemble(
            instruction="Synthesize all valid reasoning chains into a single, precise answer. Ensure the answer is factually correct and directly addresses the question.",
            contexts_list=summarized_chains
        )

        return final_answer