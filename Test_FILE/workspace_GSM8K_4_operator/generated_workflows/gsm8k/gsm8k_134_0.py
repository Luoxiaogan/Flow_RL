# Workflow ID: gsm8k_134_0
# Benchmark: gsm8k
# Data Indices: [279, 177]

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
            instruction="""Extract all key information from the problem:
            - Identify all numbers and their units
            - Determine relationships between quantities
            - Classify the problem type (e.g., sequential operations, rate problems)
            - Highlight what the question is asking for
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Problem Type Classification
        problem_type = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Classify the problem into one of the following categories:
            1. Sequential Operations
            2. Rate Problems
            3. Distribution
            4. Proportions
            5. Multi-entity Tracking
            Provide a clear classification.""",
            context=initial_analysis
        )

        # Step 3: Conditional Branching Based on Problem Type
        if "sequential" in problem_type.lower():
            # Sequential Operations Workflow
            steps = await self.generate(
                instruction=f"""Given the problem type:
                {problem_type}
                
                Break the problem into sequential steps:
                - List each calculation required
                - Specify dependencies between steps
                - Ensure units are consistent""",
                context=initial_analysis
            )
            intermediate_results = []
            for step in steps.split('\n'):
                result = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show all intermediate results and validate units.""",
                    context="\n".join(intermediate_results)
                )
                intermediate_results.append(result)
            solution = intermediate_results[-1]

        elif "rate" in problem_type.lower():
            # Rate Problems Workflow
            solution = await self.generate(
                instruction=f"""Solve the rate problem:
                {problem_type}
                
                Use the relationship: Distance = Speed × Time
                - Identify given values
                - Perform necessary conversions
                - Calculate the unknown""",
                context=initial_analysis
            )

        elif "distribution" in problem_type.lower():
            # Distribution Workflow
            solution = await self.generate(
                instruction=f"""Solve the distribution problem:
                {problem_type}
                
                Divide quantities equally or proportionally:
                - Identify total quantity
                - Determine distribution criteria
                - Calculate individual shares""",
                context=initial_analysis
            )

        elif "proportions" in problem_type.lower():
            # Proportions Workflow
            solution = await self.generate(
                instruction=f"""Solve the proportion problem:
                {problem_type}
                
                Use ratios, percentages, or fractions:
                - Identify known proportions
                - Set up equations
                - Solve for the unknown""",
                context=initial_analysis
            )

        elif "multi-entity" in problem_type.lower():
            # Multi-entity Tracking Workflow
            solution = await self.generate(
                instruction=f"""Track quantities for multiple entities:
                {problem_type}
                
                - Identify entities and their quantities
                - Perform calculations for each entity
                - Combine results as needed""",
                context=initial_analysis
            )

        else:
            # Default Workflow
            solution = await self.generate(
                instruction=f"""Solve the problem using general methods:
                {problem_type}
                
                - Perform calculations step-by-step
                - Validate intermediate results
                - Ensure units are consistent""",
                context=initial_analysis
            )

        # Step 4: Ensemble Synthesis
        alternative_solutions = await asyncio.gather(
            self.generate(instruction="Solve using an alternative method...", context=initial_analysis),
            self.generate(instruction="Solve using estimation...", context=initial_analysis)
        )
        final_solution = await self.ensemble(
            instruction="Compare solutions and select the most accurate one.",
            contexts_list=[solution] + alternative_solutions
        )

        # Step 5: Final Validation
        validated_solution = await self.revise(
            instruction="Verify the final solution for accuracy and completeness.",
            context=final_solution
        )

        return validated_solution