# Workflow ID: gsm8k_101_0
# Benchmark: gsm8k
# Data Indices: [156, 98]

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
        import re

        # Step 1: Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Identify the type of problem (e.g., rate, distribution, proportion) and any constraints. 
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Classify the problem and determine solution strategy
        classification = await self.generate(
            instruction=f"""Based on the following analysis:
            {initial_analysis}
            
            Classify the problem into one of the following categories:
            - Sequential Operations
            - Rate Problems
            - Distribution
            - Proportions
            - Multi-entity
            
            Suggest a primary solution strategy and any alternative approaches.""",
            context=initial_analysis
        )

        # Step 3: Generate multiple solution paths in parallel
        primary_solution = await self.generate(
            instruction=f"""Using the primary strategy identified:
            {classification}
            
            Solve the problem step-by-step, showing all calculations and intermediate results.""",
            context=initial_analysis
        )

        alternative_solution = await self.generate(
            instruction=f"""Using an alternative strategy identified:
            {classification}
            
            Solve the problem step-by-step, showing all calculations and intermediate results.""",
            context=initial_analysis
        )

        # Step 4: Validate and refine solutions
        validated_primary = await self.revise(
            instruction="Check for errors and improve clarity in the primary solution.",
            context=primary_solution
        )

        validated_alternative = await self.revise(
            instruction="Check for errors and improve clarity in the alternative solution.",
            context=alternative_solution
        )

        # Step 5: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="Compare the primary and alternative solutions. Select the most accurate and complete one.",
            contexts_list=[validated_primary, validated_alternative]
        )

        # Step 6: Summarize and extract the final answer
        summary = await self.summarize(
            instruction="Condense the solution into a concise format, highlighting the final numerical answer.",
            context=final_solution
        )

        # Extract the final numerical answer using regex
        match = re.search(r'\b\d+(\.\d+)?\b', summary)
        final_answer = float(match.group()) if match else None

        return final_answer