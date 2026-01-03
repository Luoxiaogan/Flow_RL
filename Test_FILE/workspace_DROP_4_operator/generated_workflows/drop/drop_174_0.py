# Workflow ID: drop_174_0
# Benchmark: drop
# Data Indices: [195, 492]

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

        # Step 1: Initial Analysis - Classify problem type and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the question type (arithmetic, counting, comparison, span extraction).
            2. Extract all entities, numbers, and relationships mentioned in the passage.
            3. Map pronouns and partial names to specific entities.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Processing - Extract entities, numbers, and resolve references
        entities_task = self.generate(
            instruction="Extract all named entities (people, teams, places) from the passage.",
            context=initial_analysis
        )
        numbers_task = self.generate(
            instruction="Extract all numbers and their contexts from the passage.",
            context=initial_analysis
        )
        references_task = self.generate(
            instruction="Resolve pronouns and partial names to specific entities.",
            context=initial_analysis
        )
        entities, numbers, references = await asyncio.gather(entities_task, numbers_task, references_task)

        # Step 3: Operation Identification and Execution
        operation_plan = await self.generate(
            instruction=f"""Based on the question and extracted information:
            Entities: {entities}
            Numbers: {numbers}
            References: {references}
            
            Identify the required operation(s) and describe how to execute them step-by-step.""",
            context=initial_analysis
        )

        # Conditional Branching for Operation Execution
        if "subtraction" in operation_plan.lower():
            result = await self.generate(
                instruction=f"""Perform subtraction based on the following:
                Entities: {entities}
                Numbers: {numbers}
                References: {references}
                
                Show all steps and provide the final result.""",
                context=operation_plan
            )
        elif "addition" in operation_plan.lower():
            result = await self.generate(
                instruction=f"""Perform addition based on the following:
                Entities: {entities}
                Numbers: {numbers}
                References: {references}
                
                Show all steps and provide the final result.""",
                context=operation_plan
            )
        elif "counting" in operation_plan.lower():
            result = await self.generate(
                instruction=f"""Count instances based on the following:
                Entities: {entities}
                Numbers: {numbers}
                References: {references}
                
                Show all steps and provide the final result.""",
                context=operation_plan
            )
        else:
            result = await self.generate(
                instruction=f"""Extract the exact text span based on the following:
                Entities: {entities}
                Numbers: {numbers}
                References: {references}
                
                Ensure the answer matches the passage exactly.""",
                context=operation_plan
            )

        # Step 4: Validation and Refinement
        validated_result = await self.revise(
            instruction="Validate the result for accuracy and completeness. Fix any errors.",
            context=result
        )

        # Step 5: Final Answer Synthesis
        final_answer = await self.ensemble(
            instruction="Synthesize the final answer. Ensure it matches the expected format.",
            contexts_list=[validated_result, operation_plan, initial_analysis]
        )

        return final_answer