# Workflow ID: mbpp_77_0
# Benchmark: mbpp
# Data Indices: [285]

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

        # Step 1: Extract function name and requirements
        analysis = await self.generate(
            instruction="""Extract the function name, input types, and expected behavior from the problem text and test cases. 
            Focus on identifying:
            - The function name from the assert statements
            - Input types and their structure
            - Expected output format and behavior
            Provide a structured summary.""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Clarify and refine the extracted information, ensuring all requirements are understood.",
            context=analysis
        )

        # Step 2: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Based on the refined analysis:
            {refined_analysis}
            
            Generate an initial Python solution that satisfies the requirements. Include:
            - Proper imports
            - Correct function name and signature
            - Implementation of the core logic
            Ensure the code is complete and executable.""",
            context=refined_analysis
        )
        validated_solution = await self.revise(
            instruction="Validate the solution against the test cases and improve clarity and correctness.",
            context=initial_solution
        )

        # Step 3: Parallel exploration of alternatives
        alternative_solutions = await asyncio.gather(
            self.generate(
                instruction="Explore an alternative solution using a different algorithm or approach.",
                context=refined_analysis
            ),
            self.generate(
                instruction="Explore another alternative solution focusing on edge cases and robustness.",
                context=refined_analysis
            )
        )
        best_solution = await self.ensemble(
            instruction="Compare the initial solution and alternative solutions, selecting the best one based on correctness and clarity.",
            contexts_list=[validated_solution] + alternative_solutions
        )

        # Step 4: Iterative refinement
        final_solution = best_solution
        for _ in range(3):  # Maximum 3 iterations
            feedback = await self.generate(
                instruction="Identify any remaining issues or improvements needed in the solution.",
                context=final_solution
            )
            if "no issues" in feedback.lower():
                break
            final_solution = await self.revise(
                instruction=f"Refine the solution based on feedback: {feedback}",
                context=final_solution
            )

        # Step 5: Final validation and summarization
        final_validation = await self.revise(
            instruction="Perform a final validation of the solution, ensuring it passes all test cases and handles edge cases.",
            context=final_solution
        )
        summary = await self.summarize(
            instruction="Summarize the final solution and its rationale in a clear and concise format.",
            context=final_validation
        )

        return summary