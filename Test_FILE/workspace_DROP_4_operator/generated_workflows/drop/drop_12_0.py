# Workflow ID: drop_12_0
# Benchmark: drop
# Data Indices: [291, 297]

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
        
        # Initial analysis: Extract entities and numbers
        entities_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Format as structured list with clear categories.""",
            context=""
        )
        
        # Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities from the passage:
            Passage Entities: {entities_numbers}
            
            Provide mapping of references to specific entities.""",
            context=entities_numbers
        )
        
        # Identify required operations based on question phrasing
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation(s) to answer the question based on its phrasing:
            Resolved References: {resolved_references}
            
            Possible operations include:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span Extraction
            
            Specify the exact operation(s) needed.""",
            context=resolved_references
        )
        
        # Conditional branching based on operation type
        if "arithmetic" in operation_identification.lower():
            arithmetic_operations = await asyncio.gather(
                self.generate(instruction="Perform addition operations...", context=operation_identification),
                self.generate(instruction="Perform subtraction operations...", context=operation_identification)
            )
            result = await self.ensemble(
                instruction="Combine arithmetic results into final answer...",
                contexts_list=arithmetic_operations
            )
        elif "counting" in operation_identification.lower():
            count_result = await self.generate(
                instruction="Count occurrences of specified items...",
                context=operation_identification
            )
            result = count_result
        elif "comparison" in operation_identification.lower():
            comparison_result = await self.generate(
                instruction="Compare values or attributes as specified...",
                context=operation_identification
            )
            result = comparison_result
        elif "span extraction" in operation_identification.lower():
            span_result = await self.generate(
                instruction="Extract exact text spans matching criteria...",
                context=operation_identification
            )
            result = span_result
        else:
            # Default comprehensive approach
            result = await self.generate(
                instruction="Apply general problem-solving framework...",
                context=operation_identification
            )
        
        # Iterative refinement loop
        for _ in range(3):
            validation = await self.generate(
                instruction=f"Validate the correctness of: {result}",
                context=result
            )
            if "error" in validation.lower() or "incorrect" in validation.lower():
                result = await self.revise(
                    instruction=f"Revise based on validation feedback: {validation}",
                    context=result
                )
            else:
                break
        
        return result