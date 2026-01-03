# Workflow ID: drop_61_0
# Benchmark: drop
# Data Indices: [412, 489]

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

        # Step 1: Initial Analysis - Extract entities and classify question type
        initial_analysis = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships from the passage:
                - Entities: Names, places, organizations
                - Numbers: Values and what they represent
                - Relationships: Connections between entities and numbers
                Format as a structured list.""",
                context=""
            ),
            self.generate(
                instruction="""Classify the question type:
                - Arithmetic (addition, subtraction, etc.)
                - Counting (how many times, how many different)
                - Comparison (greater/less, first/last)
                - Span Extraction (who, what, when)
                Provide clear reasoning for the classification.""",
                context=""
            )
        )
        entities_context, question_type_context = initial_analysis

        # Step 2: Parallel Exploration - Resolve references, identify numbers, determine operations
        parallel_tasks = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve all references in the question to specific entities in the passage:
                Passage: {entities_context}
                Question: {question_type_context}
                Ensure pronouns and partial names are mapped correctly.""",
                context=entities_context
            ),
            self.generate(
                instruction=f"""Identify all relevant numbers and their contexts:
                Passage: {entities_context}
                Question: {question_type_context}
                Include units, descriptions, and relationships.""",
                context=entities_context
            ),
            self.generate(
                instruction=f"""Determine the required operation(s) based on the question type:
                Passage: {entities_context}
                Question: {question_type_context}
                Specify arithmetic steps, counting criteria, or comparison logic.""",
                context=question_type_context
            )
        )
        resolved_references, relevant_numbers, required_operations = parallel_tasks

        # Step 3: Synthesis and Validation
        synthesis = await self.ensemble(
            instruction="""Synthesize the following into a unified understanding:
            - Resolved references
            - Relevant numbers and contexts
            - Required operations
            Ensure consistency and completeness.""",
            contexts_list=[resolved_references, relevant_numbers, required_operations]
        )

        # Step 4: Final Computation and Formatting
        final_answer = await self.generate(
            instruction=f"""Perform the required operation(s) and format the answer:
            Unified Understanding: {synthesis}
            Follow the expected format: number, date, or exact text span.""",
            context=synthesis
        )

        return final_answer