# Workflow ID: hotpotqa_24_0
# Benchmark: hotpotqa
# Data Indices: [44, 297]

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
            1. Bridge Question: Connects documents through shared entities.
            2. Comparison Question: Compares properties across documents.
            3. Compositional Question: Combines multiple facts to derive an answer.
            Provide a clear classification with justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        documents = await self.generate(
            instruction="Extract all named entities, relationships, and key facts from each document.",
            context=""
        )
        entities_list = documents.split("\n\n")  # Assume each document's extraction is separated by double newlines

        # Step 3: Identify bridge entities or comparable attributes
        if "Bridge Question" in question_type:
            bridge_entities = await asyncio.gather(
                *[self.generate(
                    instruction=f"Identify bridge entities in: {doc}",
                    context=""
                ) for doc in entities_list]
            )
            reasoning_chain = await self.generate(
                instruction=f"Connect bridge entities: {bridge_entities} to form a reasoning chain.",
                context=""
            )
        elif "Comparison Question" in question_type:
            comparable_attributes = await asyncio.gather(
                *[self.generate(
                    instruction=f"Identify comparable attributes in: {doc}",
                    context=""
                ) for doc in entities_list]
            )
            reasoning_chain = await self.generate(
                instruction=f"Compare attributes: {comparable_attributes} to determine the relationship.",
                context=""
            )
        else:  # Compositional Question
            reasoning_steps = await asyncio.gather(
                *[self.generate(
                    instruction=f"Extract reasoning steps from: {doc}",
                    context=""
                ) for doc in entities_list]
            )
            reasoning_chain = await self.generate(
                instruction=f"Combine reasoning steps: {reasoning_steps} into a coherent chain.",
                context=""
            )

        # Step 4: Synthesize the final answer
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"Derive an answer from reasoning chain: {reasoning_chain}",
                context=""
            ) for _ in range(3)]  # Generate multiple candidates
        )
        final_answer = await self.ensemble(
            instruction="Select the most factually supported answer.",
            contexts_list=candidate_answers
        )

        # Step 5: Validate and refine the answer
        validation = await self.generate(
            instruction=f"Validate the answer: {final_answer} against the supporting facts.",
            context=reasoning_chain
        )
        refined_answer = await self.revise(
            instruction="Improve clarity and ensure factual accuracy.",
            context=validation
        )

        return refined_answer