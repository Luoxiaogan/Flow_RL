# Workflow ID: gsm8k_42_0
# Benchmark: gsm8k
# Data Indices: [0, 35]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract and classify key information:
            - Identify all numerical values and their context
            - Classify the problem type (e.g., rate, distribution, proportions)
            - Highlight any constraints or conditions
            - Determine the expected answer format""",
            context=""
        )

        # Step 2: Parallel Exploration
        exploration_tasks = [
            self.generate(
                instruction=f"""Develop solution using direct calculation:
                - Follow step-by-step reasoning
                - Show all intermediate results
                - Maintain numerical precision""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop solution using estimation techniques:
                - Approximate values where necessary
                - Validate estimates against known constraints
                - Adjust as needed for accuracy""",
                context=initial_analysis
            )
        ]
        exploration_results = await asyncio.gather(*exploration_tasks)

        # Step 3: Iterative Refinement
        refined_solutions = []
        for result in exploration_results:
            for _ in range(3):  # Limit iterations to prevent infinite loops
                critique = await self.revise(
                    instruction=f"""Critique the following solution:
                    - Check for logical consistency
                    - Verify numerical accuracy
                    - Identify areas for improvement""",
                    context=result
                )
                improved = await self.generate(
                    instruction=f"""Incorporate the following feedback:
                    {critique}
                    - Revise calculations as needed
                    - Clarify reasoning steps
                    - Ensure final answer is precise""",
                    context=result
                )
                if "error" not in critique.lower():
                    break
                result = improved
            refined_solutions.append(result)

        # Step 4: Final Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Select the most accurate and complete solution
            - Merge complementary insights if applicable
            - Present final answer as a single numerical value""",
            contexts_list=refined_solutions
        )

        return final_answer