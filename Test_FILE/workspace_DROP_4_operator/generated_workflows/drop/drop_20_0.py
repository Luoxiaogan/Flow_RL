# Workflow ID: drop_20_0
# Benchmark: drop
# Data Indices: [142, 6]

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
        
        # Initial Analysis: Extract all relevant entities and numbers
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Reference Resolution: Map question references to specific passage entities
        references = await self.generate(
            instruction=f"""Resolve all references in the question to specific entities in the passage.
            Passage entities: {entities}
            Question references: [pronouns, partial names, etc.]
            Provide a mapping of references to entities.""",
            context=entities
        )
        
        # Problem Classification: Identify the type of problem and required operations
        classification = await self.generate(
            instruction=f"""Classify the problem based on the question and extracted information.
            Entities: {entities}
            References: {references}
            
            Categories:
            - Arithmetic: Addition, subtraction, percentage calculation
            - Counting: How many times, how many different
            - Comparison: Greater/less than, longer/shorter
            - Span Extraction: Exact text spans
            
            Identify the category and necessary operations.""",
            context=f"{entities}\n{references}"
        )
        
        # Conditional Branching: Direct workflow based on problem type
        if "arithmetic" in classification.lower():
            # Parallel Processing: Generate multiple solution attempts
            attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve using addition:
                    Entities: {entities}
                    References: {references}
                    Perform addition and show all steps.""",
                    context=f"{entities}\n{references}"
                ),
                self.generate(
                    instruction=f"""Solve using subtraction:
                    Entities: {entities}
                    References: {references}
                    Perform subtraction and show all steps.""",
                    context=f"{entities}\n{references}"
                ),
                self.generate(
                    instruction=f"""Solve using percentage calculation:
                    Entities: {entities}
                    References: {references}
                    Perform percentage calculation and show all steps.""",
                    context=f"{entities}\n{references}"
                )
            )
            
            # Revise each attempt for accuracy
            revised_attempts = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Verify and improve the accuracy of this solution:
                    Solution: {attempt}
                    Ensure all calculations are correct and presented clearly.""",
                    context=attempt
                ) for attempt in attempts]
            )
            
            # Ensemble: Select the best solution
            final_solution = await self.ensemble(
                instruction=f"""Select the most accurate and complete solution:
                Options: {revised_attempts}
                Ensure the solution matches the expected format.""",
                contexts_list=revised_attempts
            )
        elif "counting" in classification.lower():
            # Similar structure for counting problems
            final_solution = await self.generate(
                instruction=f"""Count the relevant instances:
                Entities: {entities}
                References: {references}
                Perform counting and show all steps.""",
                context=f"{entities}\n{references}"
            )
        elif "comparison" in classification.lower():
            # Similar structure for comparison problems
            final_solution = await self.generate(
                instruction=f"""Compare the relevant values:
                Entities: {entities}
                References: {references}
                Perform comparison and show all steps.""",
                context=f"{entities}\n{references}"
            )
        else:
            # Default comprehensive approach for span extraction and other types
            final_solution = await self.generate(
                instruction=f"""Extract the exact text span:
                Entities: {entities}
                References: {references}
                Perform span extraction and ensure it matches the passage exactly.""",
                context=f"{entities}\n{references}"
            )
        
        # Iterative Refinement: Validate and refine the solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                Solution: {final_solution}
                Check for errors and suggest improvements.""",
                context=final_solution
            )
            
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"""Fix issues in the solution:
                    Issues: {validation}
                    Correct the solution and ensure accuracy.""",
                    context=final_solution
                )
            else:
                break
        
        # Final Answer Formatting
        formatted_answer = await self.generate(
            instruction=f"""Format the final answer:
            Solution: {final_solution}
            Ensure the answer matches the expected format (number, date, text span).""",
            context=final_solution
        )
        
        return formatted_answer