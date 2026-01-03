# Workflow ID: drop_190_0
# Benchmark: drop
# Data Indices: [430, 285]

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

        # Step 1: Initial Analysis - Extract entities and analyze the question
        extraction_task = self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Format as a structured list:
            - Entities: [names, roles, organizations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )
        question_analysis_task = self.generate(
            instruction="""Analyze the question to determine:
            - Type of problem (arithmetic, counting, comparison, etc.)
            - Required operation(s) (addition, subtraction, span extraction, etc.)
            - Expected answer format (number, date, text span)""",
            context=""
        )
        entities, question_analysis = await asyncio.gather(extraction_task, question_analysis_task)

        # Step 2: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Passage entities: {entities}
            Question: {question_analysis}
            Map all ambiguous references to their most likely entities.""",
            context=entities
        )

        # Step 3: Operation Execution
        operation_tasks = []
        if "count" in question_analysis.lower():
            operation_tasks.append(
                self.generate(
                    instruction=f"""Count the occurrences of the specified entity/event:
                    Passage: {self.problem_text}
                    Resolved references: {resolved_references}""",
                    context=resolved_references
                )
            )
        elif "add" in question_analysis.lower() or "total" in question_analysis.lower():
            operation_tasks.append(
                self.generate(
                    instruction=f"""Perform addition on the specified numbers:
                    Passage: {self.problem_text}
                    Resolved references: {resolved_references}""",
                    context=resolved_references
                )
            )
        elif "subtract" in question_analysis.lower() or "difference" in question_analysis.lower():
            operation_tasks.append(
                self.generate(
                    instruction=f"""Perform subtraction on the specified numbers:
                    Passage: {self.problem_text}
                    Resolved references: {resolved_references}""",
                    context=resolved_references
                )
            )
        elif "compare" in question_analysis.lower():
            operation_tasks.append(
                self.generate(
                    instruction=f"""Compare the specified values:
                    Passage: {self.problem_text}
                    Resolved references: {resolved_references}""",
                    context=resolved_references
                )
            )
        elif "extract" in question_analysis.lower():
            operation_tasks.append(
                self.generate(
                    instruction=f"""Extract the exact text span matching the question:
                    Passage: {self.problem_text}
                    Resolved references: {resolved_references}""",
                    context=resolved_references
                )
            )
        operation_results = await asyncio.gather(*operation_tasks)

        # Step 4: Validation and Refinement
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the result:
                Original result: {result}
                Ensure correctness and proper formatting.""",
                context=result
            ) for result in operation_results]
        )

        # Step 5: Final Answer Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize the final answer from the refined results:
            Ensure it matches the expected format and is derived from the passage.""",
            contexts_list=refined_results
        )

        return final_answer