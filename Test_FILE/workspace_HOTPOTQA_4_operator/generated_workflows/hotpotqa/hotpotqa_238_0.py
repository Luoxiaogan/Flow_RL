# Workflow ID: hotpotqa_238_0
# Benchmark: hotpotqa
# Data Indices: [195, 333]

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
            instruction="""Classify the question type:
            - Is it a bridge question (connecting entities across documents)?
            - Is it a comparison question (comparing properties)?
            - Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entity_extraction = await self.generate(
            instruction=f"""Extract all named entities and relationships from the documents:
            - Named entities: People, places, dates, etc.
            - Relationships: How entities are connected.
            Question Type: {classification}""",
            context=""
        )
        refined_entities = await self.revise(
            instruction="Refine the extracted entities and relationships to resolve ambiguities.",
            context=entity_extraction
        )

        # Step 3: Construct reasoning chains
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain for the question:
                - Start from the question entity.
                - Follow relationships to connect documents.
                Extracted Entities: {refined_entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Construct an alternative reasoning chain:
                - Explore different connections between entities.
                Extracted Entities: {refined_entities}""",
                context=""
            )
        )
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain based on evidence.",
            contexts_list=reasoning_chains
        )

        # Step 4: Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is factually correct.
            - Include supporting facts.
            Best Chain: {best_chain}""",
            context=""
        )
        validated_answer = await self.revise(
            instruction="Validate the extracted answer for factual accuracy and precision.",
            context=answer_extraction
        )

        return validated_answer