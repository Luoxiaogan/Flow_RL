# Workflow ID: hotpotqa_278_0
# Benchmark: hotpotqa
# Data Indices: [65, 292]

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

        # Step 1: Classify the question type and extract key entities/relationships
        classification = await self.generate(
            instruction="""Classify the question type and extract key entities/relationships:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities (people, places, organizations, numbers).
            - Extract relationships between entities.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel exploration of reasoning chains
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted entities/relationships:
                {classification}
                
                Build a reasoning chain starting from Document 1.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using the extracted entities/relationships:
                {classification}
                
                Build a reasoning chain starting from Document 2.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using the extracted entities/relationships:
                {classification}
                
                Build a reasoning chain starting from Document 3.""",
                context=classification
            )
        )

        # Step 3: Synthesize and validate reasoning chains
        synthesis = await self.ensemble(
            instruction="""Compare the reasoning chains and select the most promising path:
            - Ensure factual consistency.
            - Validate against the question.
            - Identify the final document containing the answer.""",
            contexts_list=reasoning_chains
        )

        # Step 4: Extract and refine the final answer
        answer_extraction = await self.generate(
            instruction=f"""Using the synthesized reasoning chain:
            {synthesis}
            
            Extract the precise answer from the final document.
            Ensure the answer is factually correct and matches the required format.""",
            context=synthesis
        )

        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            - Verify factual correctness.
            - Ensure precision and clarity.
            - Format as a short text span or yes/no response.""",
            context=answer_extraction
        )

        return refined_answer