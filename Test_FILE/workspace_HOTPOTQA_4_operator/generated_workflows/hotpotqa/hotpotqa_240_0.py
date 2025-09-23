# Workflow ID: hotpotqa_240_0
# Benchmark: hotpotqa
# Data Indices: [416, 306]

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

        # Step 1: Analyze problem type
        problem_type = await self.generate(
            instruction="""Classify the question into one of the following categories:
            - Bridge: Requires connecting two documents via a shared entity.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive an answer.
            Provide clear justification for your classification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_and_relationships = await self.generate(
            instruction=f"""Based on the problem type ({problem_type}), extract:
            - Named entities (people, places, organizations, etc.)
            - Key relationships between entities
            - Any constraints or conditions mentioned in the problem.
            Format the output as a structured list.""",
            context=problem_type
        )

        # Step 3: Build reasoning chains across documents
        reasoning_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Using Document {i} and the extracted entities/relationships:
                    - Identify relevant facts.
                    - Connect these facts to form a reasoning chain.
                    - Ensure the chain supports answering the question.""",
                    context=entities_and_relationships
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Synthesize best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most coherent and factually supported one.
            Criteria:
            - Logical consistency
            - Factual accuracy
            - Alignment with the question type""",
            contexts_list=reasoning_chains
        )

        # Step 4: Extract and validate the answer
        raw_answer = await self.generate(
            instruction=f"""From the reasoning chain ({best_chain}), extract the precise answer span.
            Ensure it directly addresses the question and is factually correct.""",
            context=best_chain
        )

        refined_answer = await self.revise(
            instruction="""Validate the extracted answer:
            - Check alignment with supporting facts.
            - Ensure precision and factual correctness.
            - Refine wording if necessary.""",
            context=raw_answer
        )

        return refined_answer