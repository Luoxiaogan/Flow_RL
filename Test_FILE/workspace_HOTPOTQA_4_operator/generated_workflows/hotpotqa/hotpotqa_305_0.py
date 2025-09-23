# Workflow ID: hotpotqa_305_0
# Benchmark: hotpotqa
# Data Indices: [212]

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
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge: Connects documents through shared entities (e.g., "What nationality is the director of [movie]?")
            2. Comparison: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            3. Compositional: Combines multiple facts to derive an answer
            Provide the classification and explain your reasoning.""",
            context=""
        )

        # Step 2: Extract key entities and relationships
        entities = await self.generate(
            instruction=f"""Given the question type: {question_type}
            Extract all named entities, relationships, and constraints from the context documents:
            - Entities: Names, titles, and roles
            - Relationships: How entities are connected
            - Constraints: Explicit or implicit conditions in the question
            Format as a structured list.""",
            context=question_type
        )

        # Step 3: Build the reasoning chain
        reasoning_chain_tasks = []
        for entity in entities.split("\n"):
            reasoning_chain_tasks.append(
                self.generate(
                    instruction=f"""Find the document(s) containing the entity: {entity}
                    Identify how this entity connects to the question and other entities.
                    Build a reasoning chain that links the documents.""",
                    context=entities
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_chain_tasks)

        # Step 4: Synthesize the reasoning chains
        synthesized_chain = await self.ensemble(
            instruction="Combine the reasoning chains into a coherent path leading to the answer.",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Using the reasoning chain: {synthesized_chain}
            Extract the precise answer from the final document.
            Ensure the answer is factually correct and matches the expected format.""",
            context=synthesized_chain
        )

        # Step 6: Validate and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Validate the answer: {answer}
            Ensure it satisfies all constraints and is supported by the reasoning chain.
            Refine if necessary.""",
            context=answer
        )

        return refined_answer