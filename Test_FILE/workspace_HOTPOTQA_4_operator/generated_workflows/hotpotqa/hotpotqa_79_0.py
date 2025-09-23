# Workflow ID: hotpotqa_79_0
# Benchmark: hotpotqa
# Data Indices: [7]

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

        # Step 1: Classify the problem type
        problem_type = await self.generate(
            instruction="""Classify this question into one of the following categories:
            - Bridge: Connects entities across documents
            - Comparison: Compares properties across documents
            - Compositional: Combines multiple facts to derive an answer
            Provide the category and explain your reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract key entities and relationships from the documents:
            Problem Type: {problem_type}
            Focus on:
            - Shared entities for bridge questions
            - Numerical/temporal data for comparison questions
            - Logical connections for compositional questions
            Format as structured list with categories.""",
            context=""
        )

        # Step 3: Construct reasoning chains (parallel paths)
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain using these entities:
                Entities: {entities}
                Ensure logical consistency and connect documents.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct an alternative reasoning chain:
                Entities: {entities}
                Explore different connections or interpretations.""",
                context=entities
            )
        )

        # Step 4: Refine reasoning chains
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Refine this reasoning chain for clarity and accuracy.",
                context=path
            ) for path in reasoning_paths]
        )

        # Step 5: Extract candidate answers
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from this reasoning chain:
                Reasoning Chain: {path}
                Ensure the answer is factual and directly supported by the documents.""",
                context=path
            ) for path in refined_paths]
        )

        # Step 6: Synthesize final answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and well-supported answer.",
            contexts_list=candidate_answers
        )

        return final_answer