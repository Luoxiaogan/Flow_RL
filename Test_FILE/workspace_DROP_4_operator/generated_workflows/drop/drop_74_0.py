# Workflow ID: drop_74_0
# Benchmark: drop
# Data Indices: [457, 101]

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

        # Initial Analysis: Classify problem type and extract entities
        initial_analysis = await self.generate(
            instruction="""Classify the problem type (arithmetic, counting, comparison, span extraction, multi-step) 
            and extract all named entities, numbers, and relationships from the passage. 
            Format as structured JSON with keys: 'problem_type', 'entities', 'numbers', 'relationships'.""",
            context=""
        )

        # Parse initial analysis
        try:
            analysis = json.loads(initial_analysis)
        except json.JSONDecodeError:
            analysis = {"problem_type": "unknown", "entities": [], "numbers": [], "relationships": []}

        # Parallel Processing: Generate solutions for different problem types
        problem_type = analysis.get("problem_type", "unknown")
        entities = analysis.get("entities", [])
        numbers = analysis.get("numbers", [])
        relationships = analysis.get("relationships", [])

        if problem_type == "arithmetic":
            solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Perform arithmetic operations based on the question and extracted numbers: {numbers}.
                    Identify the required operation (addition, subtraction, etc.) and calculate the result.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Validate arithmetic operations by cross-checking with relationships: {relationships}.""",
                    context=""
                )
            )
        elif problem_type == "counting":
            solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Count occurrences of entities or events based on the question and extracted entities: {entities}.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Cross-validate counts with relationships: {relationships}.""",
                    context=""
                )
            )
        elif problem_type == "comparison":
            solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Compare entities or numbers based on the question and extracted data: {numbers}, {entities}.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Ensure comparisons align with relationships: {relationships}.""",
                    context=""
                )
            )
        elif problem_type == "span extraction":
            solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Extract the exact text span from the passage that answers the question. 
                    Use entities: {entities} and relationships: {relationships} for context.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Validate span extraction by ensuring it matches the question exactly.""",
                    context=""
                )
            )
        else:  # Multi-step or unknown
            solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Break down the problem into sub-problems and solve each step-by-step. 
                    Use entities: {entities}, numbers: {numbers}, and relationships: {relationships}.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Validate multi-step solutions by ensuring all sub-problems are addressed.""",
                    context=""
                )
            )

        # Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(instruction="Refine and validate the solution.", context=sol) for sol in solutions]
        )

        # Ensemble Decision: Synthesize the best solution
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=refined_solutions
        )

        return final_answer