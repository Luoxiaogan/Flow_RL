# Workflow ID: hotpotqa_300_0
# Benchmark: hotpotqa
# Data Indices: [61, 268]

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
        question_type_analysis = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting shared entities across documents.
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts in sequence.
            Provide the classification along with reasoning.""",
            context=""
        )

        # Step 2: Extract key entities and relationships
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from Document {i+1}.
                Focus on entities relevant to the question type: {question_type_analysis}.
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )
            for i in range(10)  # Assuming up to 10 documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the extracted entities: {entities}
                Build a reasoning chain to answer the question: {self.problem_text}.
                Ensure the chain connects entities across documents logically.""",
                context=entities
            ) for entities in extracted_entities]
        )

        # Step 4: Validate and refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine this reasoning chain:
                {chain}
                Ensure each step logically follows from the previous one and that the final answer is factually correct.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Select the best reasoning chain
        final_answer = await self.ensemble(
            instruction="""Evaluate the following reasoning chains and select the most plausible one:
            - Consider factual accuracy, logical coherence, and alignment with the question type.
            - If multiple chains are equally plausible, synthesize them into a unified answer.""",
            contexts_list=refined_chains
        )

        # Step 6: Summarize the final answer
        summarized_answer = await self.summarize(
            instruction="Condense the final answer into a short, factual response.",
            context=final_answer
        )

        return summarized_answer