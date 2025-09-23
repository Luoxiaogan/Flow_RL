# Workflow ID: drop_227_0
# Benchmark: drop
# Data Indices: [476, 254]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Classify the question type (arithmetic, counting, comparison, span extraction). 
            Provide structured output with categories:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]
            - Question Type: [classification]""",
            context=""
        )

        # Step 2: Reference Resolution
        resolved_references = await self.revise(
            instruction="Resolve all pronouns and partial names to specific entities in the passage.",
            context=initial_analysis
        )

        # Step 3: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Based on the question phrasing, identify the required operation(s):
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, etc.
            - Span Extraction: Exact text spans.
            Context: {resolved_references}""",
            context=resolved_references
        )

        # Step 4: Parallel Execution
        if "arithmetic" in operation_identification.lower():
            # Extract numbers and perform calculations
            numbers = re.findall(r'\d+\.?\d*', resolved_references)
            numbers = [float(num) for num in numbers]
            
            if "subtraction" in operation_identification.lower():
                result = numbers[0] - numbers[1]
            elif "addition" in operation_identification.lower():
                result = sum(numbers)
            else:
                result = "Unknown arithmetic operation"
        elif "span extraction" in operation_identification.lower():
            # Extract relevant text span
            result = await self.generate(
                instruction="Identify the exact text span that answers the question.",
                context=resolved_references
            )
        else:
            # Default case for other operations
            result = await self.generate(
                instruction="Perform the required operation based on the identified type.",
                context=operation_identification
            )

        # Step 5: Validation and Refinement
        final_answer = await self.revise(
            instruction="Validate the result and ensure it matches the expected format.",
            context=result
        )

        return final_answer