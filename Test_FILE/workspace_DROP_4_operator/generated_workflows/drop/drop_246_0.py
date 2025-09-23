# Workflow ID: drop_246_0
# Benchmark: drop
# Data Indices: [262, 449]

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

        # Step 1: Initial Analysis (Parallel Extraction and Classification)
        extraction, classification = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships from the passage. 
                Format as a structured list with categories:
                - Entities: [names, roles]
                - Numbers: [values, what they represent]
                - Relationships: [connections between entities]""",
                context=""
            ),
            self.generate(
                instruction="""Classify the question type:
                - Is it arithmetic, counting, comparison, or span extraction?
                - What specific operation(s) are required?
                - What is the expected answer format?""",
                context=""
            )
        )

        # Step 2: Reference Resolution
        resolved_references = await self.revise(
            instruction=f"""Resolve all question references to specific entities in the passage:
            Passage entities: {extraction}
            Question: {self.problem_text}
            
            Ensure all pronouns and partial names are mapped correctly.""",
            context=classification
        )

        # Step 3: Operation Execution (Conditional Branching)
        if "arithmetic" in classification.lower():
            # Construct and solve equations
            equation = await self.generate(
                instruction=f"""Based on the resolved references and extracted numbers:
                Resolved references: {resolved_references}
                Extracted numbers: {extraction}
                
                Construct the required arithmetic equation and solve it step-by-step.""",
                context=resolved_references
            )
            result = await self.revise(
                instruction="Verify the arithmetic solution for correctness and plausibility.",
                context=equation
            )
        elif "span extraction" in classification.lower():
            # Generate multiple candidates and select the best
            candidates = await asyncio.gather(
                self.generate(instruction="Find the first candidate span matching the question.", context=resolved_references),
                self.generate(instruction="Find the second candidate span matching the question.", context=resolved_references),
                self.generate(instruction="Find the third candidate span matching the question.", context=resolved_references)
            )
            result = await self.ensemble(
                instruction="Select the best candidate span that exactly matches the passage.",
                contexts_list=candidates
            )
        else:
            # Default comprehensive approach
            result = await self.generate(
                instruction=f"""Solve the problem using the following information:
                Resolved references: {resolved_references}
                Extracted numbers: {extraction}
                
                Provide a clear and concise solution.""",
                context=resolved_references
            )

        # Step 4: Iterative Refinement
        validation = await self.generate(
            instruction=f"""Validate the result:
            Result: {result}
            Expected format: {classification}
            
            Identify any inconsistencies or errors.""",
            context=result
        )
        if "error" in validation.lower():
            refined_result = await self.revise(
                instruction=f"Fix issues identified during validation: {validation}",
                context=result
            )
            result = refined_result

        # Step 5: Final Synthesis
        final_answer = await self.summarize(
            instruction="Condense the reasoning process and present the final answer in the required format.",
            context=result
        )

        return final_answer