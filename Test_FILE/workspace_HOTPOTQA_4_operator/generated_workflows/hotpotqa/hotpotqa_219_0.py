# Workflow ID: hotpotqa_219_0
# Benchmark: hotpotqa
# Data Indices: [382]

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
            instruction="""Classify the question into one of three categories:
            1. Bridge Question: Connects shared entities across documents.
            2. Comparison Question: Compares properties or attributes.
            3. Compositional Question: Combines multiple facts to derive an answer.
            Analyze the question structure and provide the classification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the documents:
            - Entities: Names, organizations, locations, etc.
            - Relationships: Connections between entities (e.g., 'governing body for').
            Focus on entities mentioned in the question and their connections.
            Question Type: {question_type}""",
            context=""
        )
        refined_entities = await self.revise(
            instruction="Ensure completeness and accuracy of extracted entities and relationships.",
            context=entities
        )

        # Step 3: Build reasoning chains (parallel exploration)
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain for a bridge question:
                - Find shared entities between documents.
                - Trace relationships to connect entities.
                Entities: {refined_entities}""",
                context=refined_entities
            ),
            self.generate(
                instruction=f"""Construct a reasoning chain for a comparison question:
                - Extract comparable attributes from documents.
                - Evaluate attributes to determine the answer.
                Entities: {refined_entities}""",
                context=refined_entities
            ),
            self.generate(
                instruction=f"""Construct a reasoning chain for a compositional question:
                - Combine multiple facts to derive the answer.
                - Ensure logical consistency.
                Entities: {refined_entities}""",
                context=refined_entities
            )
        )
        reasoning_chain = await self.ensemble(
            instruction="Synthesize multiple reasoning paths into a coherent chain.",
            contexts_list=reasoning_paths
        )

        # Step 4: Extract the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            - Identify the exact answer span.
            - Ensure factual correctness by cross-referencing with supporting facts.
            Reasoning Chain: {reasoning_chain}""",
            context=reasoning_chain
        )
        validated_answer = await self.revise(
            instruction="Validate the answer for factual correctness and precision.",
            context=answer
        )

        return validated_answer