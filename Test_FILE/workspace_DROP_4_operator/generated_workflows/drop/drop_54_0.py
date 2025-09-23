# Workflow ID: drop_54_0
# Benchmark: drop
# Data Indices: [80, 27]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Classify the problem type (numerical, textual, multi-hop) and identify the required operation(s).
            Format the output as follows:
            - Entities: [list of entities]
            - Numbers: [list of numbers and their contexts]
            - Problem Type: [numerical/textual/multi-hop]
            - Required Operations: [addition/subtraction/comparison/span-extraction/etc.]""",
            context=""
        )

        # Step 2: Dynamic Branching - Handle different problem types
        if "numerical" in initial_analysis.lower():
            # Numerical Problems: Perform arithmetic operations
            numerical_solution = await self.generate(
                instruction=f"""Based on the extracted information:
                {initial_analysis}
                
                Perform the required arithmetic operations step-by-step.
                Validate each calculation and present the final result.""",
                context=initial_analysis
            )
            refined_solution = await self.revise(
                instruction="Double-check calculations and ensure correct formatting.",
                context=numerical_solution
            )
            return refined_solution
        
        elif "textual" in initial_analysis.lower():
            # Textual Problems: Extract exact spans
            textual_solution = await self.generate(
                instruction=f"""Based on the extracted information:
                {initial_analysis}
                
                Identify the exact text span that answers the question.
                Ensure the span matches the passage exactly.""",
                context=initial_analysis
            )
            refined_solution = await self.revise(
                instruction="Verify the extracted span matches the passage exactly.",
                context=textual_solution
            )
            return refined_solution
        
        elif "multi-hop" in initial_analysis.lower():
            # Multi-Hop Problems: Combine multiple pieces of information
            multi_hop_steps = await self.generate(
                instruction=f"""Based on the extracted information:
                {initial_analysis}
                
                Break the problem into sub-steps and solve each step sequentially.
                Combine the results to form the final answer.""",
                context=initial_analysis
            )
            refined_solution = await self.revise(
                instruction="Ensure all sub-steps are logically connected and the final answer is coherent.",
                context=multi_hop_steps
            )
            return refined_solution
        
        else:
            # Default Comprehensive Approach
            default_solution = await self.generate(
                instruction=f"""Based on the extracted information:
                {initial_analysis}
                
                Solve the problem using a general reasoning framework.
                Validate the solution against the passage.""",
                context=initial_analysis
            )
            refined_solution = await self.revise(
                instruction="Refine the solution for clarity and accuracy.",
                context=default_solution
            )
            return refined_solution