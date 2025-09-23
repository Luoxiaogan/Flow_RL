# Workflow ID: gsm8k_54_0
# Benchmark: gsm8k
# Data Indices: [3, 5]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, their context, and relationships:
            - Identify entities (people, objects, etc.)
            - List all numbers and their units
            - Describe relationships between numbers
            Format as structured JSON.""",
            context=""
        )

        # Step 2: Identify solution path
        solution_path = await self.generate(
            instruction=f"""Based on the extracted information:
            {extraction}
            
            Propose a step-by-step solution path:
            - List all calculations in order
            - Show dependencies between steps
            - Highlight intermediate results""",
            context=extraction
        )

        # Step 3: Validate and refine solution path
        refined_path = await self.revise(
            instruction="""Check the solution path for errors:
            - Ensure all calculations are correct
            - Verify dependencies are respected
            - Suggest improvements if needed""",
            context=solution_path
        )

        # Step 4: Perform parallel computations if applicable
        steps = refined_path.split("\n")
        independent_steps = [step for step in steps if "independent" in step.lower()]
        if independent_steps:
            parallel_results = await asyncio.gather(
                *[self.generate(instruction=f"Perform calculation: {step}", context=refined_path) 
                  for step in independent_steps]
            )
            combined_results = "\n".join(parallel_results)
        else:
            combined_results = refined_path

        # Step 5: Iterative refinement
        final_solution = combined_results
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction="Validate the solution and identify errors.",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=final_solution
                )
            else:
                break

        # Step 6: Extract final answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return final_answer