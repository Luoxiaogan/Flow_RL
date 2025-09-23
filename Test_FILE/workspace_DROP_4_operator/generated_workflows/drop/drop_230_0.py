# Workflow ID: drop_230_0
# Benchmark: drop
# Data Indices: [152, 464]

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

        # Step 1: Extract all relevant information from the passage
        extracted_info = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: Named entities (people, places, organizations)
            - Numbers: Any numerical values and their context
            - Relationships: How entities and numbers are related
            Format as a structured list with clear categories.""",
            context=""
        )

        # Step 2: Analyze the question to classify its type and identify required operations
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            Passage Context: {extracted_info}
            
            Classify the question into one of the following categories:
            1. Arithmetic (addition, subtraction, etc.)
            2. Counting (how many times, how many different, etc.)
            3. Comparison (greater/less than, earlier/later, etc.)
            4. Span Extraction (who did, what was, when did, etc.)
            5. Multi-step (requires chaining multiple operations)
            
            Identify the required operations and any constraints.""",
            context=extracted_info
        )

        # Step 3: Propose solutions in parallel based on the identified operations
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using arithmetic operations:
                Passage Context: {extracted_info}
                Question Analysis: {question_analysis}
                
                Perform any required addition, subtraction, multiplication, or division.
                Ensure calculations are precise and match the expected format.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using counting:
                Passage Context: {extracted_info}
                Question Analysis: {question_analysis}
                
                Count occurrences, entities, or events as required.
                Ensure counts are accurate and match the expected format.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using comparison:
                Passage Context: {extracted_info}
                Question Analysis: {question_analysis}
                
                Compare numbers, dates, or other entities as required.
                Ensure comparisons are logical and match the expected format.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using span extraction:
                Passage Context: {extracted_info}
                Question Analysis: {question_analysis}
                
                Extract exact text spans that answer the question.
                Ensure spans match the passage exactly.""",
                context=question_analysis
            )
        )

        # Step 4: Validate and refine the proposed solutions
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the proposed solution:
                Passage Context: {extracted_info}
                Question Analysis: {question_analysis}
                
                Check for accuracy, completeness, and correctness.
                Correct any errors or omissions.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 5: Synthesize the best solution or combine insights
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the best solution:
            Passage Context: {extracted_info}
            Question Analysis: {question_analysis}
            
            Evaluate all refined solutions and select the most accurate and complete answer.
            If multiple solutions are valid, synthesize them into a unified response.""",
            contexts_list=refined_solutions
        )

        return final_answer