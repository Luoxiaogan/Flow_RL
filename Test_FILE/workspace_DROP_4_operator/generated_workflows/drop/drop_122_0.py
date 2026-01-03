# Workflow ID: drop_122_0
# Benchmark: drop
# Data Indices: [184, 329]

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

        # Step 1: Initial Analysis (Extract entities and classify problem type)
        extract_entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: Names, teams, roles
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and connections
            Format as structured list.""",
            context=""
        )
        classify_problem_task = self.generate(
            instruction="""Classify the problem type:
            - Arithmetic: Addition, subtraction, comparison
            - Counting: Number of instances
            - Comparison: Greater/less than, first/last
            - Span Extraction: Exact text matching
            Provide classification and reasoning.""",
            context=""
        )
        entities, problem_type = await asyncio.gather(extract_entities_task, classify_problem_task)

        # Step 2: Entity Resolution
        resolved_entities = await self.revise(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Original entities: {entities}
            Ensure clarity and completeness.""",
            context=entities
        )

        # Step 3: Operation Execution
        if "arithmetic" in problem_type.lower():
            operation_result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                Entities: {resolved_entities}
                Problem type: {problem_type}
                Execute required calculations.""",
                context=resolved_entities
            )
        elif "counting" in problem_type.lower():
            operation_result = await self.generate(
                instruction=f"""Count instances:
                Entities: {resolved_entities}
                Problem type: {problem_type}
                Count relevant instances.""",
                context=resolved_entities
            )
        elif "comparison" in problem_type.lower():
            operation_result = await self.generate(
                instruction=f"""Compare values:
                Entities: {resolved_entities}
                Problem type: {problem_type}
                Perform required comparisons.""",
                context=resolved_entities
            )
        elif "span extraction" in problem_type.lower():
            operation_result = await self.generate(
                instruction=f"""Extract exact text span:
                Entities: {resolved_entities}
                Problem type: {problem_type}
                Match question requirements.""",
                context=resolved_entities
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Solve using general reasoning:
                Entities: {resolved_entities}
                Problem type: {problem_type}
                Provide solution.""",
                context=resolved_entities
            )

        # Step 4: Answer Synthesis
        synthesized_answer = await self.summarize(
            instruction=f"""Condense results into final answer:
            Operation result: {operation_result}
            Format according to question requirements.""",
            context=operation_result
        )

        # Step 5: Validation and Refinement
        validated_answer = await self.revise(
            instruction=f"""Validate answer:
            Synthesized answer: {synthesized_answer}
            Ensure correctness and format compliance.""",
            context=synthesized_answer
        )

        return validated_answer