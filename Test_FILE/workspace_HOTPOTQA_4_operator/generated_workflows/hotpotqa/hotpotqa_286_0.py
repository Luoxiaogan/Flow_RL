# Workflow ID: hotpotqa_286_0
# Benchmark: hotpotqa
# Data Indices: [100]

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
        
        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify the question type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Identify all key entities mentioned in the question.
            3. Suggest potential documents that might contain relevant information.
            Provide structured output with clear labels.""",
            context=""
        )
        
        # Step 2: Parallel Entity Exploration - Explore each entity's context
        entities = await self.generate(
            instruction="Extract all named entities and their roles from the question.",
            context=initial_analysis
        )
        entity_explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"Explore the context of entity: {entity} in the documents. "
                            f"Identify relevant facts and relationships.",
                context=initial_analysis
            ) for entity in entities.split('\n') if entity.strip()]
        )
        
        # Step 3: Reasoning Chain Construction - Synthesize explorations into a chain
        reasoning_chain = await self.ensemble(
            instruction="Synthesize the entity explorations into a coherent reasoning chain. "
                        "Ensure logical connections between facts from different documents.",
            contexts_list=entity_explorations
        )
        
        # Step 4: Answer Extraction and Validation - Extract precise answer
        final_answer = await self.revise(
            instruction="Extract the precise answer from the reasoning chain. "
                        "Ensure it matches the expected format (short text span or yes/no). "
                        "Validate the answer against supporting facts.",
            context=reasoning_chain
        )
        
        return final_answer