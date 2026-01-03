# Workflow ID: drop_220_0
# Benchmark: drop
# Data Indices: [205, 292]

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
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Reference Resolution - Map pronouns and partial names to specific entities
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Given these extracted entities and relationships:
            {initial_analysis}
            
            Identify and map:
            - Pronouns to their antecedents
            - Partial names to full names
            - Implicit references to explicit entities""",
            context=initial_analysis
        )

        # Step 3: Operation Identification - Determine the required operation(s) based on the question
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question:
            Given the resolved references:
            {resolved_references}
            
            Determine:
            - Type of operation (addition, subtraction, counting, comparison, span extraction)
            - Relevant numbers/entities involved
            - Expected answer format (number, date, text span)""",
            context=resolved_references
        )

        # Step 4: Parallel Execution - Generate multiple potential solutions using different methods
        parallel_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using arithmetic operations:
                Given the identified operation:
                {operation_identification}
                
                Perform necessary calculations and provide the answer.""",
                context=operation_identification
            ),
            self.generate(
                instruction=f"""Solve using span extraction:
                Given the identified operation:
                {operation_identification}
                
                Extract the exact text span that answers the question.""",
                context=operation_identification
            ),
            self.generate(
                instruction=f"""Solve using logical reasoning:
                Given the identified operation:
                {operation_identification}
                
                Reason through the problem and provide the answer.""",
                context=operation_identification
            )
        )

        # Step 5: Synthesis and Selection - Choose the best solution or synthesize a comprehensive answer
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution:
            Given these potential solutions:
            {parallel_solutions}
            
            Select the most accurate and complete answer, considering:
            - Correctness of calculations
            - Exactness of text spans
            - Logical consistency""",
            contexts_list=parallel_solutions
        )

        # Step 6: Final Revision - Ensure the answer is accurate, complete, and formatted correctly
        final_answer = await self.revise(
            instruction=f"""Finalize the answer:
            Given the synthesized solution:
            {synthesized_solution}
            
            Ensure:
            - Accuracy of the answer
            - Completeness of information
            - Correct formatting (number, date, text span)""",
            context=synthesized_solution
        )

        return final_answer