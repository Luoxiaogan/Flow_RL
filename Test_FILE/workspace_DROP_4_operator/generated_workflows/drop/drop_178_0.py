# Workflow ID: drop_178_0
# Benchmark: drop
# Data Indices: [351, 346]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?
            Provide structured classification.""",
            context=""
        )

        # Step 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=initial_analysis
        )

        # Step 3: Operation Identification
        operation = await self.generate(
            instruction=f"""Given the question and extracted entities:
            {entities}
            
            Identify the required operation(s):
            - Addition, subtraction, counting, comparison, etc.
            - Map question phrasing to specific operation(s).""",
            context=entities
        )

        # Step 4: Parallel Computation
        computations = await asyncio.gather(
            self.generate(instruction="Perform addition if required...", context=operation),
            self.generate(instruction="Perform subtraction if required...", context=operation),
            self.generate(instruction="Perform counting if required...", context=operation),
            self.generate(instruction="Perform comparison if required...", context=operation)
        )

        # Step 5: Validation and Refinement
        validated_results = await asyncio.gather(
            *[self.revise(instruction="Validate and refine computation...", context=c) for c in computations]
        )

        # Step 6: Answer Synthesis
        final_answer = await self.ensemble(
            instruction="Synthesize validated results into final answer...",
            contexts_list=validated_results
        )

        return final_answer