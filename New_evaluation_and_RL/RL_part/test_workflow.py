<code>
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
        import asyncio
        initial_solution = await self.generate(instruction="""
        You are a highly skilled reasoning engine for reading comprehension. Your task is to solve a complex question based on a provided passage.

        Follow these strict, step-by-step instructions to arrive at the final answer:
        1.  **Analyze the Question:** Carefully read the question and determine its intent. Identify the key entities, events, or numbers being asked about. What specific operation is required (e.g., counting, comparison, arithmetic, span extraction)?
        2.  **Extract All Relevant Information:** Scour the entire passage and extract every piece of information (numbers, dates, names, relationships) that is relevant to the question you identified in the previous step. Be exhaustive; do not miss any details.
        3.  **Perform Reasoning:** Based on the extracted information, perform the necessary reasoning or calculation. Show your work. If it's a comparison, state which item is greater/less. If it's a calculation, list the numbers and the operation. If it's a fact, state the fact directly.
        4.  **Formulate the Final Answer:** Synthesize your reasoning into a clear, concise final answer. The answer should directly address the question and nothing else. Do not include any extra text, just the final answer itself.""",context=self.problem_text)

        final_answer = await self.revise(instruction=f"""
        You have received a potential answer to a reading comprehension problem.
        The answer is: "{initial_solution}"

        Your task is to critically review and refine this answer.
        1.  Check if the answer directly and accurately addresses the original question.
        2.  Verify that the reasoning leading to the answer is sound and fully supported by the passage.
        3.  Ensure the answer is in the correct format (e.g., a number, a date, a text span).
        4.  If the answer is correct, provide it as is. If it's incorrect or incomplete, provide the corrected answer.
        5.  Your final output must be ONLY the answer itself, with no additional explanation, reasoning, or formatting.""",context=initial_solution)

        return final_answer
</code>