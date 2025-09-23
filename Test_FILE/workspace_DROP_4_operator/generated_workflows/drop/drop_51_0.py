# Workflow ID: drop_51_0
# Benchmark: drop
# Data Indices: [123, 432]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify all entities, numbers, and relationships in the passage.
            - Classify the problem type (numerical, textual, comparative).
            - Determine the required operation(s) based on the question phrasing.
            Provide structured output with clear labels.""",
            context=""
        )

        # Phase 2: Parallel Fact Extraction
        entities_task = self.generate(
            instruction=f"""Extract all named entities and their relationships:
            {analysis}
            Focus on entities relevant to the question.""",
            context=analysis
        )
        numbers_task = self.generate(
            instruction=f"""Extract all numbers and their contexts:
            {analysis}
            Include units and what each number represents.""",
            context=analysis
        )
        spans_task = self.generate(
            instruction=f"""Extract relevant text spans:
            {analysis}
            Focus on spans matching the question's focus.""",
            context=analysis
        )
        entities, numbers, spans = await asyncio.gather(entities_task, numbers_task, spans_task)

        # Phase 3: Operation Execution
        operation_results = []
        if "numerical" in analysis.lower():
            operation_results.append(await self.generate(
                instruction=f"""Perform numerical operations:
                {numbers}
                Execute the required operation(s) identified in the analysis.""",
                context=numbers
            ))
        if "textual" in analysis.lower():
            operation_results.append(await self.generate(
                instruction=f"""Extract exact text spans:
                {spans}
                Ensure spans match the question's focus exactly.""",
                context=spans
            ))
        if "comparative" in analysis.lower():
            operation_results.append(await self.generate(
                instruction=f"""Compare entities:
                {entities}
                Identify the entity satisfying the comparison criteria.""",
                context=entities
            ))

        # Phase 4: Validation and Refinement
        validated_results = []
        for result in operation_results:
            validated = await self.revise(
                instruction=f"""Validate and refine:
                {result}
                Ensure the result matches the expected format and constraints.""",
                context=result
            )
            validated_results.append(validated)

        # Phase 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            Consider all validated results and choose the one that best answers the question.
            If multiple answers are valid, select the most precise or comprehensive one.""",
            contexts_list=validated_results
        )

        return final_answer