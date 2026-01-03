# Workflow ID: drop_86_0
# Benchmark: drop
# Data Indices: [158, 286]

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
        
        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 2: Reference Resolution - Resolve pronouns and partial names
        reference_mappings = await asyncio.gather(
            self.generate(instruction="Generate potential mappings for references...", context=initial_analysis),
            self.generate(instruction="Generate alternative mappings for ambiguous references...", context=initial_analysis)
        )
        resolved_references = await self.ensemble(
            instruction="Select the most accurate reference mappings...",
            contexts_list=reference_mappings
        )
        refined_references = await self.revise(
            instruction="Refine and verify the selected reference mappings...",
            context=resolved_references
        )
        
        # Step 3: Problem Classification and Operation Identification
        problem_classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            Entities and References: {refined_references}
            
            Identify:
            - Problem Type (Arithmetic, Counting, Comparison, Span Extraction)
            - Required Operations (Addition, Subtraction, etc.)
            - Expected Answer Format""",
            context=initial_analysis
        )
        
        # Step 4: Operation Execution - Perform the required calculations
        if "arithmetic" in problem_classification.lower():
            calculation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operations:
                Entities and References: {refined_references}
                
                Show all steps and maintain full precision.""",
                context=problem_classification
            )
        elif "counting" in problem_classification.lower():
            calculation_result = await self.generate(
                instruction=f"""Count the required instances:
                Entities and References: {refined_references}
                
                Ensure all instances are counted accurately.""",
                context=problem_classification
            )
        else:
            calculation_result = await self.generate(
                instruction=f"""Execute the required operations:
                Entities and References: {refined_references}
                
                Follow the identified problem type and operations.""",
                context=problem_classification
            )
        
        # Step 5: Answer Formatting - Ensure the answer matches the expected format
        formatted_answer = await self.revise(
            instruction=f"""Format the answer according to the expected format:
            Calculation Result: {calculation_result}
            
            Ensure the answer is a number, date, or exact text span as required.""",
            context=problem_classification
        )
        
        return formatted_answer