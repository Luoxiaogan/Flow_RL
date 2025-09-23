# Workflow ID: hotpotqa_151_0
# Benchmark: hotpotqa
# Data Indices: [354, 277]

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
            instruction="""Classify the question type:
            - Bridge: Requires connecting entities across documents.
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts.
            Analyze the question structure and provide a clear classification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract key entities and their relationships:
            - Identify named entities (e.g., species, genera, people).
            - Highlight relationships between entities (e.g., 'belongs to', 'is greater than').
            Context: {question_type}""",
            context=""
        )
        refined_entities = await self.revise(
            instruction="Refine extracted entities and relationships for accuracy.",
            context=entities
        )

        # Step 3: Build reasoning chains (parallel exploration)
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain for the {question_type} question:
                - Trace relationships between entities.
                - Synthesize information from multiple documents.
                Entities: {refined_entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Construct an alternative reasoning chain:
                - Explore different connections between entities.
                - Consider alternative interpretations of the question.
                Entities: {refined_entities}""",
                context=""
            )
        )

        # Step 4: Validate and synthesize reasoning chains
        validated_chain = await self.ensemble(
            instruction="""Select the most robust reasoning chain:
            - Ensure all facts are supported by context documents.
            - Prioritize chains with clear, logical connections.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract and validate the answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is factually correct.
            - Format as a short text span or yes/no response.
            Reasoning Chain: {validated_chain}""",
            context=""
        )
        final_answer = await self.revise(
            instruction="Validate the answer against supporting facts and refine if necessary.",
            context=answer
        )

        return final_answer