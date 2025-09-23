# Workflow ID: hotpotqa_18_0
# Benchmark: hotpotqa
# Data Indices: [490, 19]

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
            instruction="""Analyze the problem structure:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities and relationships.
            3. Outline potential reasoning chains.""",
            context=""
        )
        
        # Step 2: Parallel Processing - Generate multiple reasoning chains and potential answers
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the initial analysis: {initial_analysis}
                Generate a reasoning chain focusing on bridge entities.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the initial analysis: {initial_analysis}
                Generate a reasoning chain focusing on comparison properties.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the initial analysis: {initial_analysis}
                Generate a reasoning chain focusing on compositional facts.""",
                context=initial_analysis
            )
        )
        
        # Step 3: Validation and Refinement - Validate each chain and refine the answers
        refined_answers = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this reasoning chain: {chain}",
                context=chain
            ) for chain in reasoning_chains]
        )
        
        # Step 4: Synthesis - Use ensemble methods to select the best answer
        final_answer = await self.ensemble(
            instruction="""Evaluate all refined answers:
            1. Check factual correctness.
            2. Ensure answer is supported by documents.
            3. Select the most precise and relevant answer.""",
            contexts_list=refined_answers
        )
        
        return final_answer