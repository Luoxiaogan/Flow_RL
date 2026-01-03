# Workflow ID: hotpotqa_23_0
# Benchmark: hotpotqa
# Data Indices: [458, 241]

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
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Extract named entities (people, places, organizations) from the question.
            - Identify potential bridge entities that connect documents.
            Provide structured output with clear categories.""",
            context=""
        )
        
        # Step 2: Bridge Entity Identification
        bridge_entities = await asyncio.gather(
            *[self.generate(
                instruction=f"""Identify and evaluate potential bridge entities:
                - Match entities from the question with those in the documents.
                - Assess relevance based on context.
                Focus on: {entity}""",
                context=analysis
            ) for entity in ["Jimmy Hoffa", "Massachusetts", "Apple Pay"]]  # Example entities
        )
        
        # Step 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct reasoning chains using bridge entity: {entity}
                - Link facts from different documents.
                - Ensure logical consistency.
                Provide detailed chain.""",
                context=analysis
            ) for entity in bridge_entities]
        )
        best_chain = await self.ensemble(
            instruction="Synthesize the best reasoning chain based on relevance and consistency.",
            contexts_list=reasoning_chains
        )
        
        # Step 4: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the relevant document(s):
            - Locate the exact sentence or phrase that answers the question.
            - Verify using supporting facts from other documents.
            Reasoning chain: {best_chain}""",
            context=analysis
        )
        refined_answer = await self.revise(
            instruction="Refine the extracted answer for clarity and accuracy.",
            context=answer
        )
        
        return refined_answer