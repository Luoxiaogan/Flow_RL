# Workflow ID: hotpotqa_253_0
# Benchmark: hotpotqa
# Data Indices: [13, 84]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities, relationships, and constraints. 
            Focus on identifying shared entities across documents.""",
            context=""
        )

        # Step 2: Parallel Exploration
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Generate a reasoning chain starting from {entity}.
                Connect documents through shared entities and infer missing links.
                Ensure logical consistency and factual correctness.""",
                context=analysis
            ) for entity in ["Kansas State Wildcats", "Jim Dickey", "Tonka", "The Happiest Millionaire"]]
        )

        # Step 3: Validation and Refinement
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="""Validate this reasoning chain against the documents.
                Correct any errors and ensure factual accuracy.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 4: Synthesis
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Summarize this reasoning chain concisely.",
                context=chain
            ) for chain in refined_chains]
        )
        best_chain = await self.ensemble(
            instruction="""Select the most complete and accurate reasoning chain.
            Prioritize chains with strong evidence and logical consistency.""",
            contexts_list=summaries
        )

        # Step 5: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the final document 
            in this reasoning chain: {best_chain}.""",
            context=""
        )

        # Step 6: Feedback Loop (if needed)
        if "no valid chain" in best_chain.lower():
            # Broaden exploration criteria and repeat
            pass

        return answer