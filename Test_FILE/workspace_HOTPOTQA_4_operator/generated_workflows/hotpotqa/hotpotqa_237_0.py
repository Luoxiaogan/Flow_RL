# Workflow ID: hotpotqa_237_0
# Benchmark: hotpotqa
# Data Indices: [300, 379]

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
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Determine the reasoning chain required to answer the question.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Entity Extraction
        entities = await self.generate(
            instruction=f"""Extract named entities and relationships from the context documents:
            - Entities: Names, organizations, dates, etc.
            - Relationships: Connections between entities.
            Focus on entities relevant to the reasoning chain identified in:
            {analysis}""",
            context=""
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain:
            - Start with the question: {self.problem_text}
            - Use the entities and relationships: {entities}
            - Connect facts from different documents step by step.
            Ensure logical coherence and factual accuracy.""",
            context=entities
        )

        # Step 4: Answer Extraction
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Focus on the final document in the chain.
            - Provide a short text span or yes/no response.
            Reasoning chain: {reasoning_chain}""",
            context=reasoning_chain
        )

        # Step 5: Validation and Refinement
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Check against supporting facts in the reasoning chain.
            - Refine if necessary to ensure accuracy.
            Extracted answer: {answer}""",
            context=reasoning_chain
        )

        # Step 6: Dynamic Adaptation (Optional)
        alternative_answers = await asyncio.gather(
            self.generate(instruction="Explore alternative reasoning chains...", context=entities),
            self.generate(instruction="Consider conflicting information...", context=entities)
        )
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer based on evidence and coherence.",
            contexts_list=[validated_answer] + alternative_answers
        )

        return final_answer