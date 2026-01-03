# Workflow ID: hotpotqa_194_0
# Benchmark: hotpotqa
# Data Indices: [398, 101]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract all named entities (people, places, organizations).
            3. Identify relationships between entities.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Processing - Gather facts about entities
        entities = await self.generate(
            instruction="Extract all named entities from the initial analysis.",
            context=initial_analysis
        )
        entity_list = entities.split('\n')  # Simplistic parsing for demonstration

        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"Find all relevant facts about {entity} from the documents.",
                context=initial_analysis
            ) for entity in entity_list]
        )

        # Step 3: Reasoning Chain Construction - Synthesize facts into a chain
        reasoning_chain = await self.ensemble(
            instruction="Combine the extracted facts into a coherent reasoning chain.",
            contexts_list=document_facts
        )

        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity and logical consistency.",
            context=reasoning_chain
        )

        # Step 4: Answer Extraction and Validation
        answer = await self.generate(
            instruction="Extract the final answer from the reasoning chain.",
            context=refined_chain
        )

        validated_answer = await self.revise(
            instruction="Validate the answer against the supporting facts in the documents.",
            context=answer
        )

        return validated_answer