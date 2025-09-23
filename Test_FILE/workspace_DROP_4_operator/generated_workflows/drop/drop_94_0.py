# Workflow ID: drop_94_0
# Benchmark: drop
# Data Indices: [51, 215]

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
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the question type (arithmetic, counting, comparison, etc.)
            - Extract key entities and relationships
            - Highlight any ambiguities or missing information
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the passage:
            - Format as a structured list with categories (People, Places, Numbers, Actions)
            - Resolve any direct references within the passage
            Based on this analysis: {analysis}""",
            context=analysis
        )

        # Step 3: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            - Use the extracted entities: {entities}
            - Ensure all references in the question are mapped to passage entities
            Provide a clear mapping.""",
            context=entities
        )

        # Step 4: Operation Identification
        operations = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question:
            - Classify the operation type (addition, subtraction, comparison, etc.)
            - Provide detailed instructions for execution
            Entities and references: {resolved_references}""",
            context=resolved_references
        )

        # Step 5: Execution (Parallel Exploration)
        execution_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform the identified operation(s):
                - Execute calculations or comparisons
                - Extract exact text spans if needed
                Instructions: {operations}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Explore alternative interpretations of the question:
                - Consider different mappings or operations
                - Validate against the passage
                Instructions: {operations}""",
                context=resolved_references
            )
        )

        # Step 6: Synthesis and Validation
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the candidates:
            - Ensure the answer matches the expected format
            - Validate against the passage
            - Choose the most accurate and complete response""",
            contexts_list=execution_results
        )

        # Step 7: Adaptive Refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the final answer:
            - Check for format mismatches or logical inconsistencies
            - Suggest refinements if necessary
            Final Answer: {final_answer}""",
            context=final_answer
        )

        if "error" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the final answer based on validation feedback:
                - Correct format issues
                - Address logical inconsistencies
                Feedback: {validation}""",
                context=final_answer
            )
            return refined_answer

        return final_answer