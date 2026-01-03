# Workflow ID: drop_76_0
# Benchmark: drop
# Data Indices: [230, 444]

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
        
        # Phase 1: Initial Analysis and Entity Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list with categories.""",
            context=""
        )
        
        # Phase 2: Question Understanding and Operation Identification
        analysis = await self.generate(
            instruction=f"""Analyze the question to determine:
            - Required operation(s): addition, subtraction, counting, comparison, etc.
            - References: map pronouns and partial names to specific entities from: {entities}
            - Expected answer format: number, date, or text span""",
            context=entities
        )
        
        # Phase 3: Parallel Execution of Identified Operations
        operations = analysis.split("\n")
        operation_results = await asyncio.gather(
            *[self.generate(instruction=op, context=entities) for op in operations if op.strip()]
        )
        
        # Phase 4: Validation and Formatting
        validated_results = await asyncio.gather(
            *[self.revise(instruction=f"Validate and format result: {res}", context=entities) for res in operation_results]
        )
        
        # Phase 5: Ensemble Decision
        final_answer = await self.ensemble(
            instruction="Evaluate the following options and select the best answer:",
            contexts_list=validated_results
        )
        
        return final_answer