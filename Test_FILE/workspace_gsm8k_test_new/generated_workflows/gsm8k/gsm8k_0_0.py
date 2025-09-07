# Workflow ID: gsm8k_0_0
# Benchmark: gsm8k
# Data Indices: [0]

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

        # Step 1: Extract all numerical values and their context
        extraction_instruction = (
            "Extract all numerical values and their associated context from the problem. "
            "Include units, relationships, and any relevant descriptive information. "
            "Format the output as a list of key-value pairs where keys describe the context."
        )
        extracted_data = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Formulate a step-by-step solution strategy
        reasoning_instruction = (
            f"Given the extracted data: {extracted_data}, determine the sequence of calculations "
            "required to solve the problem. Identify the relationships between numbers and "
            "formulate a clear, logical plan. Include intermediate steps and their expected outcomes."
        )
        solution_strategy = await self.generate(instruction=reasoning_instruction, context=self.problem_text)

        # Step 3: Perform calculations step-by-step
        calculation_instruction = (
            f"Execute the following solution strategy step-by-step: {solution_strategy}. "
            "Perform each calculation explicitly and track intermediate results. "
            "Ensure numerical accuracy at each step."
        )
        calculations = await self.generate(instruction=calculation_instruction, context=self.problem_text)

        # Step 4: Revise and validate intermediate results
        revision_instruction = (
            f"Review the calculations: {calculations}. Check for logical consistency and numerical accuracy. "
            "If errors are found, revise the reasoning chain and correct the calculations."
        )
        revised_solution = await self.revise(instruction=revision_instruction, context=calculations)

        # Step 5: Summarize the final answer
        summarization_instruction = (
            f"Condense the revised solution: {revised_solution} into a single numerical answer. "
            "Ensure the final result is precise and formatted correctly."
        )
        final_answer = await self.summarize(instruction=summarization_instruction, context=revised_solution)

        return final_answer