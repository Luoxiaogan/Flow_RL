# Workflow ID: drop_0_0
# Benchmark: drop
# Data Indices: [1, 0]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        """
        import asyncio

        # Step 1: Extract key information (numbers, entities, relationships)
        extraction_instruction = (
            "Extract all numerical values, entities, and relationships from the passage. "
            "Include any relevant dates, counts, names, or descriptive phrases. "
            "Organize the information clearly so it can be used for reasoning."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Understand the question intent
        question_analysis_instruction = (
            "Analyze the question to determine the type of reasoning required. "
            "Classify the question as one of the following: arithmetic operation, counting, comparison, selection, or span extraction. "
            "Outline the specific steps needed to answer the question based on the extracted information."
        )
        question_analysis = await self.generate(instruction=question_analysis_instruction, context=self.problem_text)

        # Step 3: Perform reasoning based on question type
        reasoning_instruction_template = (
            "Using the extracted information and the question analysis, perform the required reasoning steps. "
            "For arithmetic operations, calculate the result explicitly. "
            "For counting, tally the occurrences of the specified entity or event. "
            "For comparisons, evaluate which entity satisfies the condition. "
            "For selection, identify the correct entity or span based on the question. "
            "Provide a clear and concise answer."
        )

        # Parallelize reasoning steps if multiple approaches are possible
        reasoning_results = await asyncio.gather(
            self.generate(instruction=f"{reasoning_instruction_template}", context=extracted_info),
            self.generate(instruction=f"{reasoning_instruction_template}", context=question_analysis)
        )

        # Step 4: Synthesize final answer
        synthesis_instruction = (
            "Evaluate the provided reasoning results and synthesize a final answer. "
            "Ensure the answer is accurate, complete, and directly addresses the question. "
            "If there are discrepancies between the results, resolve them logically."
        )
        final_answer = await self.ensemble(instruction=synthesis_instruction, contexts=reasoning_results)

        # Optional Step 5: Refine the answer if needed
        refinement_instruction = (
            "Review the final answer for clarity, accuracy, and completeness. "
            "Make any necessary refinements based on the original problem text and extracted information."
        )
        refined_answer = await self.revise(instruction=refinement_instruction, context=final_answer)

        return refined_answer