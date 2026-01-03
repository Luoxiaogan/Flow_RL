# Workflow ID: hotpotqa_109_0
# Benchmark: hotpotqa
# Data Indices: [248]

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
        import re

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Entity Search - Find entities in all documents
        entities = re.findall(r'\b[A-Z][A-Za-z\s]+\b', initial_analysis)  # Simplified entity extraction
        entity_searches = await asyncio.gather(
            *[self.generate(
                instruction=f"Search for entity '{entity}' in all documents and extract relevant sentences.",
                context=""
            ) for entity in entities]
        )

        # Step 3: Reasoning Chain Construction - Synthesize information
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from multiple documents:
            1. Connect entities across documents.
            2. Build a logical chain of reasoning.
            3. Highlight supporting facts.""",
            contexts_list=entity_searches
        )

        # Step 4: Answer Extraction - Extract precise answer
        answer = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer to the question. Ensure it is factually correct and supported by evidence.""",
            context=""
        )

        # Step 5: Validation and Refinement - Validate and refine the answer
        validated_answer = await self.revise(
            instruction="""Validate the answer:
            1. Check factual correctness.
            2. Ensure proper format (yes/no or short text span).
            3. Refine if necessary.""",
            context=answer
        )

        return validated_answer