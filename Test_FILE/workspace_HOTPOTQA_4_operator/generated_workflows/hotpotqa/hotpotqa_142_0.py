# Workflow ID: hotpotqa_142_0
# Benchmark: hotpotqa
# Data Indices: [156]

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
        
        # Step 1: Classify the question type
        classification = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining facts)?
            Provide structured classification.""",
            context=""
        )
        
        # Step 2: Extract entities and relationships
        entities_extraction = await self.generate(
            instruction=f"""Based on the classification: {classification}
            Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 3: Build reasoning chains
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""For entities: {entities_extraction}
                Build reasoning chains connecting them across documents.
                Follow these steps:
                1. Identify bridge entities
                2. Trace relationships
                3. Formulate logical connections""",
                context=entities_extraction
            ),
            self.generate(
                instruction=f"""For entities: {entities_extraction}
                Explore alternative reasoning paths.
                Consider:
                - Different document combinations
                - Alternative interpretations""",
                context=entities_extraction
            )
        )
        
        # Step 4: Synthesize reasoning chains
        synthesized_reasoning = await self.ensemble(
            instruction="Synthesize all reasoning chains into a coherent path.",
            contexts_list=reasoning_chains
        )
        
        # Step 5: Refine and validate the reasoning
        refined_reasoning = await self.revise(
            instruction="Refine the reasoning chain for clarity and accuracy.",
            context=synthesized_reasoning
        )
        
        # Step 6: Extract and summarize the answer
        answer_extraction = await self.summarize(
            instruction=f"""From the refined reasoning: {refined_reasoning}
            Extract the precise answer span.
            Ensure:
            - Factual correctness
            - Exact phrasing from the text""",
            context=refined_reasoning
        )
        
        return answer_extraction