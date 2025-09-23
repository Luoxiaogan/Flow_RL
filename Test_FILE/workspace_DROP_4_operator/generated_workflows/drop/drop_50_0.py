# Workflow ID: drop_50_0
# Benchmark: drop
# Data Indices: [72, 356]

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

        # Step 1: Extract entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all ambiguous terms in the question to specific entities in the passage.
            Passage Entities:
            {entities}
            
            Question:
            [Extract question from the problem text]
            
            Provide a mapping of ambiguous terms to specific entities.""",
            context=entities
        )

        # Step 3: Classify the question into an operation type
        operation_type = await self.generate(
            instruction=f"""Classify the question into one of the following operation types:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            
            Passage Entities:
            {entities}
            
            Resolved References:
            {resolved_references}
            
            Question:
            [Extract question from the problem text]""",
            context=f"{entities}

{resolved_references}"
        )

        # Step 4: Parallel processing based on operation type
        arithmetic_result, counting_result, comparison_result, span_result = await asyncio.gather(
            self.generate(
                instruction=f"""Perform arithmetic operations based on the question.
                Passage Entities:
                {entities}
                
                Resolved References:
                {resolved_references}
                
                Question:
                [Extract question from the problem text]""",
                context=f"{entities}

{resolved_references}",
            ),
            self.generate(
                instruction=f"""Count occurrences based on the question.
                Passage Entities:
                {entities}
                
                Resolved References:
                {resolved_references}
                
                Question:
                [Extract question from the problem text]""",
                context=f"{entities}

{resolved_references}",
            ),
            self.ensemble(
                instruction=f"""Compare values based on the question.
                Passage Entities:
                {entities}
                
                Resolved References:
                {resolved_references}
                
                Question:
                [Extract question from the problem text]""",
                contexts_list=[entities, resolved_references],
            ),
            self.generate(
                instruction=f"""Extract the exact text span from the passage based on the question.
                Passage:
                [Extract passage from the problem text]
                
                Resolved References:
                {resolved_references}
                
                Question:
                [Extract question from the problem text]""",
                context=f"{entities}

{resolved_references}",
            )
        )

        # Step 5: Synthesize results
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the results from the parallel branches into a single answer.
            Operation Type:
            {operation_type}
            
            Arithmetic Result:
            {arithmetic_result}
            
            Counting Result:
            {counting_result}
            
            Comparison Result:
            {comparison_result}
            
            Span Extraction Result:
            {span_result}""",
            contexts_list=[arithmetic_result, counting_result, comparison_result, span_result]
        )

        # Step 6: Refine the final answer
        refined_answer = await self.revise(
            instruction=f"""Refine the final answer to match the expected format (number, date, or text span).
            Final Answer:
            {final_answer}""",
            context=final_answer
        )

        return refined_answer