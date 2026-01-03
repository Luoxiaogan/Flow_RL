# Workflow ID: hotpotqa_81_0
# Benchmark: hotpotqa
# Data Indices: [135, 312]

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
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining facts)?
            Also, extract all named entities, numbers, and relationships mentioned in the question.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore reasoning chains based on question type
        bridge_path = await self.generate(
            instruction=f"""For bridge questions, identify shared entities and trace their relationships across documents.
            Key entities: {initial_analysis}
            Follow the logical connections to build a reasoning chain.""",
            context=initial_analysis
        )
        comparison_path = await self.generate(
            instruction=f"""For comparison questions, extract relevant properties and compare them across documents.
            Key entities: {initial_analysis}
            Focus on numerical or temporal data to determine the answer.""",
            context=initial_analysis
        )
        compositional_path = await self.generate(
            instruction=f"""For compositional questions, combine multiple facts step-by-step to derive the answer.
            Key entities: {initial_analysis}
            Ensure each step logically follows from the previous one.""",
            context=initial_analysis
        )

        # Step 3: Validation and Synthesis - Evaluate and combine results
        reasoning_paths = await asyncio.gather(
            self.revise(instruction="Refine the bridge reasoning chain for clarity and accuracy.", context=bridge_path),
            self.revise(instruction="Refine the comparison reasoning chain for clarity and accuracy.", context=comparison_path),
            self.revise(instruction="Refine the compositional reasoning chain for clarity and accuracy.", context=compositional_path)
        )
        synthesized_answer = await self.ensemble(
            instruction="Synthesize the best answer from the refined reasoning chains.",
            contexts_list=reasoning_paths
        )

        # Step 4: Final Extraction - Extract the precise answer span
        final_answer = await self.generate(
            instruction=f"""Extract the exact answer span from the synthesized reasoning chain.
            Synthesized chain: {synthesized_answer}
            Ensure the answer is factually correct and matches the expected format.""",
            context=synthesized_answer
        )

        return final_answer