# Workflow ID: hotpotqa_94_0
# Benchmark: hotpotqa
# Data Indices: [415, 271]

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
            instruction="""Classify the question into one of the following types:
            1. Bridge: Requires connecting entities across documents.
            2. Comparison: Involves comparing properties or attributes.
            3. Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract key entities from the question
        entities = await self.generate(
            instruction=f"""Extract all key entities, relationships, and numerical values from the question.
            Question Type Classification: {classification}
            Format as a structured list:
            - Entities: [list of named entities]
            - Relationships: [list of relationships]
            - Numbers: [list of numerical values]""",
            context=""
        )

        # Step 3: Search for entities in context documents (parallel processing)
        document_searches = await asyncio.gather(
            *[self.generate(
                instruction=f"""Search for the following entities in Document {i+1}:
                Entities: {entities}
                Return relevant sentences and their context.""",
                context=""
            ) for i in range(10)]  # Assuming up to 10 documents
        )

        # Step 4: Construct reasoning chain using ensemble
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize the following information into a coherent reasoning chain:
            - Combine sentences containing bridging entities.
            - Ensure the chain logically connects the question to the answer.
            - Highlight supporting facts.""",
            contexts_list=document_searches
        )

        # Step 5: Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=reasoning_chain
        )

        answer_validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            Answer: {answer_extraction}
            Ensure it is factually correct and aligns with the reasoning chain.""",
            context=reasoning_chain
        )

        # Step 6: Format the final output
        final_output = await self.generate(
            instruction=f"""Format the final output:
            Answer: {answer_validation}
            Supporting Facts: {reasoning_chain}
            Ensure compliance with the required format.""",
            context=answer_validation
        )

        return final_output