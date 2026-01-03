# Workflow ID: hotpotqa_93_0
# Benchmark: hotpotqa
# Data Indices: [404]

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
            instruction="""Classify the question into one of the following categories:
            - Bridge Question: Connects entities across documents (e.g., "What nationality is the director of [movie]?")
            - Comparison Question: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional Question: Combines multiple facts to derive an answer
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Based on the classification: {classification}
            Extract all named entities, relationships, and key facts from the documents.
            Format as structured data:
            - Entities: [names, roles, and descriptions]
            - Relationships: [connections between entities]
            - Key Facts: [important statements relevant to the question]""",
            context=""
        )

        # Step 3: Construct reasoning chain (conditional branch)
        if "bridge" in classification.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for the bridge question:
                - Identify the bridge entity connecting documents
                - Follow the chain to derive the answer
                Entities and relationships: {entities}""",
                context=""
            )
        elif "comparison" in classification.lower():
            # Parallel fork for comparison facts
            facts = await asyncio.gather(
                self.generate(instruction="Extract relevant facts from Document 1...", context=entities),
                self.generate(instruction="Extract relevant facts from Document 2...", context=entities)
            )
            reasoning_chain = await self.ensemble(
                instruction="Compare the extracted facts and construct a reasoning chain.",
                contexts_list=facts
            )
        else:  # Compositional question
            reasoning_chain = await self.generate(
                instruction=f"""Combine multiple facts to construct a reasoning chain:
                Entities and relationships: {entities}""",
                context=""
            )

        # Step 4: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning chain: {reasoning_chain}
            Ensure the answer is a short factual span or yes/no response.""",
            context=""
        )

        # Validation loop
        for _ in range(3):  # Allow up to 3 refinement attempts
            validation = await self.generate(
                instruction=f"""Validate the answer:
                - Is it factually correct?
                - Does it match the question requirements?
                Answer: {answer}""",
                context=reasoning_chain
            )
            if "valid" in validation.lower():
                break
            answer = await self.revise(
                instruction=f"""Revise the answer based on validation feedback:
                Feedback: {validation}""",
                context=answer
            )

        return answer