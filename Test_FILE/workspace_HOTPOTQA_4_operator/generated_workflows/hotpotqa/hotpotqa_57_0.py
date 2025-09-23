# Workflow ID: hotpotqa_57_0
# Benchmark: hotpotqa
# Data Indices: [98, 72]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities (people, places, organizations).
            - Highlight relationships between entities.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Entity Linking
        entities = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Identify bridge entities that connect documents:
            - Match entities across documents.
            - Find shared properties or relationships.
            List all potential bridge entities.""",
            context=analysis
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using entity:
                {entity}
                
                Trace the logical flow of information across documents:
                - Start with the question.
                - Connect through shared entities.
                - End with a potential answer.
                Provide detailed reasoning steps.""",
                context=entities
            ) for entity in entities.split('\n')]
        )

        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the reasoning chain for clarity and accuracy:
                {path}""",
                context=path
            ) for path in reasoning_paths]
        )

        # Phase 4: Answer Extraction
        answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer span from the final document:
                {path}
                
                Locate the exact sentence or phrase that answers the question.
                Ensure the answer matches the expected format (short text span or yes/no).""",
                context=path
            ) for path in refined_paths]
        )

        # Phase 5: Validation
        validated_answer = await self.ensemble(
            instruction="""Validate the answers against the evidence chain:
            - Cross-reference with supporting facts.
            - Select the most accurate and well-supported answer.
            Resolve any ambiguities.""",
            contexts_list=answers
        )

        return validated_answer