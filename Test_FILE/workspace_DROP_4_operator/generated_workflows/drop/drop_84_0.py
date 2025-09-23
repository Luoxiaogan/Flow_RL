# Workflow ID: drop_84_0
# Benchmark: drop
# Data Indices: [439, 35]

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

        # Step 1: Extract key entities, numbers, and relationships from the passage
        passage_analysis = await self.generate(
            instruction="""Extract all important information from the passage:
            - Entities (people, places, teams, etc.)
            - Numbers and their context (e.g., scores, distances, counts)
            - Relationships (who did what, when, and where)
            Format as a structured list.""",
            context=""
        )

        # Step 2: Analyze the question to determine the required operation(s)
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            Passage Analysis: {passage_analysis}
            
            Question Types:
            - Counting (e.g., 'How many field goals?')
            - Arithmetic (e.g., 'What is the total?')
            - Comparison (e.g., 'Which is greater?')
            - Span Extraction (e.g., 'Who scored?')
            
            Identify:
            - Relevant entities/numbers from the passage
            - Required operation(s)
            - Expected answer format""",
            context=passage_analysis
        )

        # Step 3: Generate multiple interpretations of the question
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret the question literally:
                Passage Analysis: {passage_analysis}
                Question Analysis: {question_analysis}""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Interpret the question broadly:
                Passage Analysis: {passage_analysis}
                Question Analysis: {question_analysis}""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Interpret the question with alternative assumptions:
                Passage Analysis: {passage_analysis}
                Question Analysis: {question_analysis}""",
                context=question_analysis
            )
        )

        # Step 4: Execute the required operation(s)
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute the required operation based on interpretation:
                Passage Analysis: {passage_analysis}
                Question Analysis: {question_analysis}
                Interpretation: {interp}""",
                context=interp
            ) for interp in interpretations]
        )

        # Step 5: Synthesize results and select the best answer
        synthesized_answer = await self.ensemble(
            instruction=f"""Synthesize multiple interpretations into one answer:
            Passage Analysis: {passage_analysis}
            Question Analysis: {question_analysis}
            Operation Results: {operation_results}
            
            Criteria:
            - Match expected answer format
            - Be consistent with passage content
            - Resolve ambiguities""",
            contexts_list=operation_results
        )

        # Step 6: Validate and refine the final answer
        final_answer = await self.revise(
            instruction=f"""Validate and refine the answer:
            Passage Analysis: {passage_analysis}
            Question Analysis: {question_analysis}
            Synthesized Answer: {synthesized_answer}
            
            Ensure:
            - Correct format (number, date, text span)
            - Exact match with passage content
            - No logical inconsistencies""",
            context=synthesized_answer
        )

        return final_answer