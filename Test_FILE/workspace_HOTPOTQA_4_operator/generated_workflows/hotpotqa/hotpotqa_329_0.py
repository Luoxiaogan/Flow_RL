# Workflow ID: hotpotqa_329_0
# Benchmark: hotpotqa
# Data Indices: [97]

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
            instruction="""Classify the question into one of the following categories:
            - Bridge Question: Requires connecting documents through a shared entity.
            - Comparison Question: Involves comparing properties across documents.
            - Compositional Question: Combines multiple facts to derive an answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities and relationships from the documents:
            - Entities: Locations, organizations, dates, etc.
            - Relationships: Connections between entities (e.g., 'X is located in Y').
            Format as a structured list and map entities to their respective documents.
            Question Type: {question_type}""",
            context=""
        )

        # Step 3: Identify bridge entities (for bridge questions)
        if "bridge" in question_type.lower():
            bridge_candidates = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Identify potential bridge entities connecting documents:
                    - Focus on entities shared across multiple documents.
                    - Validate relevance to the question.
                    Context: {entities}""",
                    context=""
                ) for _ in range(3)]  # Explore multiple hypotheses
            )
            bridge_entity = await self.ensemble(
                instruction="Select the most plausible bridge entity based on relevance and supporting evidence.",
                contexts_list=bridge_candidates
            )
        else:
            bridge_entity = ""

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain to answer the question:
            - Start from the question and trace connections through the bridge entity: {bridge_entity}.
            - Follow relationships to derive the final answer.
            Context: {entities}""",
            context=entities
        )

        # Step 5: Extract and validate the answer
        raw_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is factually correct and directly addresses the question.
            - Format as a short text span or yes/no response.
            Reasoning Chain: {reasoning_chain}""",
            context=reasoning_chain
        )
        validated_answer = await self.revise(
            instruction="""Validate the answer:
            - Check factual correctness against the documents.
            - Ensure alignment with the question and reasoning chain.
            - Correct any errors or ambiguities.""",
            context=raw_answer
        )

        return validated_answer