# Workflow ID: hotpotqa_2_0
# Benchmark: hotpotqa
# Data Indices: [91, 450]

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

        # Step 1: Classify the question type and identify key components
        analysis = await self.generate(
            instruction="""Classify the question type and identify key components:
            - Is it a bridge, comparison, or compositional question?
            - What entities are mentioned in the question?
            - What relationships or constraints are implied?
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        entities_task = self.generate(
            instruction=f"""Extract named entities, relationships, and constraints from the context documents:
            Analysis: {analysis}
            Focus on entities relevant to the question type and reasoning chain.""",
            context=""
        )
        reasoning_chain_task = self.generate(
            instruction=f"""Construct an initial reasoning chain based on the analysis:
            Analysis: {analysis}
            Identify how documents connect through shared entities.""",
            context=""
        )
        entities, reasoning_chain = await asyncio.gather(entities_task, reasoning_chain_task)

        # Step 3: Refine entities and reasoning chain
        refined_entities = await self.revise(
            instruction="Refine the extracted entities and relationships to ensure completeness and accuracy.",
            context=entities
        )
        refined_reasoning_chain = await self.revise(
            instruction="Refine the reasoning chain to ensure logical coherence and factual accuracy.",
            context=reasoning_chain
        )

        # Step 4: Explore multiple reasoning paths in parallel
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Explore reasoning path 1:
                Entities: {refined_entities}
                Reasoning Chain: {refined_reasoning_chain}""",
                context=""
            ),
            self.generate(
                instruction=f"""Explore reasoning path 2:
                Entities: {refined_entities}
                Reasoning Chain: {refined_reasoning_chain}""",
                context=""
            )
        )

        # Step 5: Synthesize the best reasoning path
        best_path = await self.ensemble(
            instruction="Select the most coherent and factually accurate reasoning path.",
            contexts_list=reasoning_paths
        )

        # Step 6: Extract and validate the final answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning path:
            Best Path: {best_path}
            Ensure the answer is factually correct and matches the expected format.""",
            context=best_path
        )

        return answer