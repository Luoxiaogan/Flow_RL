# Workflow ID: gsm8k_114_0
# Benchmark: gsm8k
# Data Indices: [190, 283]

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
        key_info = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem:
            - Numerical values: List all numbers and their units.
            - Entities: Identify people, objects, and their roles.
            - Relationships: Describe how entities interact with numbers.
            Format as structured text.""",
            context=""
        )

        # Step 2: Plan the solution
        solution_plan = await self.generate(
            instruction=f"""Based on the extracted information:
            {key_info}
            
            Plan the solution:
            - Identify intermediate steps.
            - Determine the sequence of operations.
            - Define validation criteria for each step.
            Provide a detailed plan.""",
            context=key_info
        )

        # Step 3: Execute calculations (iterative refinement)
        steps = solution_plan.split('\n')
        results = []
        for step in steps:
            if "Calculate" in step:
                calculation = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show all steps and intermediate results.""",
                    context="\n".join(results)
                )
                validation = await self.generate(
                    instruction=f"""Validate the calculation:
                    {calculation}
                    
                    Check for errors and provide feedback.""",
                    context=calculation
                )
                if "error" in validation.lower():
                    revised_calculation = await self.revise(
                        instruction=f"""Fix the following issue:
                        {validation}
                        
                        Recompute the calculation.""",
                        context=calculation
                    )
                    results.append(revised_calculation)
                else:
                    results.append(calculation)

        # Step 4: Summarize the final answer
        final_answer = await self.summarize(
            instruction="""Condense the solution into a single numerical value:
            - Include only the final answer.
            - Ensure the format matches the problem's requirements.""",
            context="\n".join(results)
        )

        return final_answer