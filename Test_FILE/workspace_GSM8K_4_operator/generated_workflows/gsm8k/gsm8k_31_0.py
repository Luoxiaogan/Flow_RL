# Workflow ID: gsm8k_31_0
# Benchmark: gsm8k
# Data Indices: [135, 13]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Initial Analysis - Extract entities, relationships, and constraints
        initial_analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify numerical values and their units
            - Determine relationships between quantities
            - Highlight any constraints or conditions
            Present the extracted information in a structured format.""",
            context=""
        )

        # Step 2: Classify Problem Type and Select Strategy
        strategy = await self.generate(
            instruction=f"""Classify the problem based on the following:
            {initial_analysis}
            
            Categories:
            - Rate problems (distance/speed/time, work rates, etc.)
            - Distribution problems (dividing quantities, sharing, etc.)
            - Proportions (percentages, fractions, ratios, scaling)
            - Sequential operations (step-by-step calculations)
            
            Select the most appropriate solution strategy and outline the steps required.""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a direct calculation approach:
                Follow the strategy outlined here:
                {strategy}
                
                Show all intermediate steps and calculations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using an alternative method:
                Consider different interpretations or approaches.
                Follow the strategy outlined here:
                {strategy}
                
                Show all intermediate steps and calculations.""",
                context=initial_analysis
            )
        )

        # Step 4: Validation and Refinement - Critique and improve each path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine the following solution:
                - Check for arithmetic errors
                - Ensure logical consistency
                - Add missing details or clarifications
                Provide the improved solution.""",
                context=path
            ) for path in solution_paths]
        )

        # Step 5: Synthesis - Combine refined solutions into a final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the refined solutions into a single, coherent answer:
            - Select the most accurate and complete solution
            - Resolve any discrepancies between paths
            - Present the final numerical answer with appropriate units.""",
            contexts_list=refined_paths
        )

        return final_answer