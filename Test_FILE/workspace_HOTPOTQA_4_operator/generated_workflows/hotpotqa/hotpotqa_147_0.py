# Workflow ID: hotpotqa_147_0
# Benchmark: hotpotqa
# Data Indices: [35, 470]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract all named entities (people, places, dates, etc.).
            3. Identify potential connections between documents.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore reasoning paths
        async def explore_bridge_question():
            return await self.generate(
                instruction=f"""For bridge questions:
                1. Identify shared entities between documents.
                2. Traverse documents to build reasoning chain.
                3. Extract intermediate facts supporting the chain.
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        
        async def explore_comparison_question():
            return await self.generate(
                instruction=f"""For comparison questions:
                1. Extract relevant properties from each document.
                2. Compare properties to determine answer.
                3. Highlight supporting evidence.
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        
        async def explore_compositional_question():
            return await self.generate(
                instruction=f"""For compositional questions:
                1. Combine multiple facts from different documents.
                2. Derive the final answer through logical synthesis.
                3. Validate intermediate steps.
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        
        # Execute parallel exploration based on question type
        if "bridge" in initial_analysis.lower():
            reasoning_paths = await asyncio.gather(explorer_bridge_question())
        elif "comparison" in initial_analysis.lower():
            reasoning_paths = await asyncio.gather(explore_comparison_question())
        else:
            reasoning_paths = await asyncio.gather(explore_compositional_question())

        # Step 3: Validation and Refinement - Iteratively refine results
        refined_results = []
        for path in reasoning_paths:
            refined = await self.revise(
                instruction="""Validate and refine reasoning:
                1. Check for logical consistency.
                2. Resolve ambiguities.
                3. Ensure alignment with supporting facts.
                Context: {path}""",
                context=path
            )
            refined_results.append(refined)

        # Step 4: Final Synthesis - Merge results into unified answer
        final_answer = await self.ensemble(
            instruction="""Synthesize results into final answer:
            1. Select the most coherent reasoning chain.
            2. Extract precise answer span.
            3. Ensure factual correctness and evidence support.
            Contexts: {refined_results}""",
            contexts_list=refined_results
        )

        return final_answer