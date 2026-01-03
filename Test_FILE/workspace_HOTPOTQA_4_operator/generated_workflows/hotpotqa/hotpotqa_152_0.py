# Workflow ID: hotpotqa_152_0
# Benchmark: hotpotqa
# Data Indices: [428, 95]

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

        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify its type:
            1. Identify key entities and relationships in the question.
            2. Determine if it's a bridge, comparison, or compositional question.
            3. Highlight potential bridge entities and their roles.
            Provide structured output.""",
            context=""
        )

        # Step 2: Entity Validation and Linking
        entities = [entity.strip() for entity in analysis.split("\n") if "entity" in entity.lower()]
        validation_tasks = [
            self.generate(
                instruction=f"""Validate entity '{entity}' by cross-referencing it with all documents:
                - Check its presence and relevance.
                - Ensure it connects multiple documents.
                Provide validation result.""",
                context=analysis
            ) for entity in entities
        ]
        validation_results = await asyncio.gather(*validation_tasks)
        validated_entities = await self.ensemble(
            instruction="Select the most relevant and validated entities.",
            contexts_list=validation_results
        )

        # Step 3: Constructing Reasoning Chains
        reasoning_chain = await self.generate(
            instruction=f"""Using validated entities: {validated_entities}
            Build a reasoning chain by connecting entities across documents:
            - Trace relationships step-by-step.
            - Synthesize relevant facts.
            - Ensure logical coherence.
            Provide detailed reasoning chain.""",
            context=validated_entities
        )

        # Step 4: Answer Extraction and Refinement
        condensed_answer = await self.summarize(
            instruction="Condense the reasoning chain into a concise answer span.",
            context=reasoning_chain
        )
        refined_answer = await self.revise(
            instruction="Refine the answer for clarity and precision. Ensure it aligns with supporting facts.",
            context=condensed_answer
        )

        return refined_answer