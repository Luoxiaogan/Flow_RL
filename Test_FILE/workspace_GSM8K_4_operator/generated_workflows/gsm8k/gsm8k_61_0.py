# Workflow ID: gsm8k_61_0
# Benchmark: gsm8k
# Data Indices: [295, 280]

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

        # Step 1: Extract key information (numerical values, entities, relationships)
        extraction = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships:
            - List all numbers with their context (e.g., 'Logan's hair is 20 inches')
            - Identify relationships between entities (e.g., 'Kate's hair is half as long as Emily's')
            - Note any constraints or conditions (e.g., 'Amanda needs to sell 80 tickets')""",
            context=""
        )

        # Step 2: Plan the solution (identify sequence of operations)
        planning = await self.generate(
            instruction=f"""Based on the extracted information:
            {extraction}
            
            Plan the solution:
            - What calculations are needed?
            - In what order should they be performed?
            - Are there any intermediate results to track?""",
            context=extraction
        )

        # Step 3: Execute calculations in parallel where possible
        steps = planning.split("\n")
        calculation_tasks = []
        for step in steps:
            if "calculation" in step.lower():
                task = self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show all steps and intermediate results.""",
                    context=extraction
                )
                calculation_tasks.append(task)
        
        intermediate_results = await asyncio.gather(*calculation_tasks)

        # Step 4: Validate and refine results
        refined_results = []
        for result in intermediate_results:
            refined = await self.revise(
                instruction=f"""Verify and improve this result:
                {result}
                
                Ensure calculations are correct and clarify any ambiguities.""",
                context=result
            )
            refined_results.append(refined)

        # Step 5: Synthesize final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the final answer:
            - Combine all refined results
            - Ensure consistency across calculations
            - Present the final numerical answer only""",
            contexts_list=refined_results
        )

        return final_answer