# Workflow ID: hotpotqa_331_0
# Benchmark: hotpotqa
# Data Indices: [171]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities (people, places, works, etc.).
            3. Identify relationships or constraints mentioned in the question.
            Provide structured output.""",
            context=""
        )

        # Step 2: Document Filtering
        relevant_docs = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Identify documents that mention the key entities or relationships.
            Rank them by relevance to the question.""",
            context=""
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct reasoning chains using the following:
                Analysis: {analysis}
                Relevant Documents: {relevant_docs}
                
                Focus on connecting entities across documents.
                Hypothesize possible connections and validate them.""",
                context=""
            ) for _ in range(3)]  # Generate multiple chains
        )

        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Refine reasoning chains to ensure logical consistency and alignment with the question.",
                context=chain
            ) for chain in reasoning_chains]
        )

        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain based on evidence and logical consistency.",
            contexts_list=refined_chains
        )

        # Step 4: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {best_chain}
            
            Include supporting facts from the relevant documents.""",
            context=""
        )

        final_answer = await self.summarize(
            instruction="Condense the answer and supporting facts into a concise format.",
            context=answer
        )

        return final_answer