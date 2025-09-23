# Workflow ID: limr_3_0
# Benchmark: limr
# Data Indices: [94, 67]

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

        # Step 1: Problem Classification
        classification = await self.generate(
            instruction="""Classify the problem into one or more categories:
            - Geometry, Number Theory, Algebra, Combinatorics, Probability, Optimization, etc.
            Identify key components such as variables, constraints, and relationships.
            Provide structured output for further processing.""",
            context=""
        )

        # Step 2: Sub-Problem Decomposition
        decomposition = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Decompose the problem into sub-problems:
            - List each sub-problem and its dependencies.
            - Identify potential solution strategies for each sub-problem.
            Format as a structured list for parallel exploration.""",
            context=classification
        )

        # Step 3: Parallel Exploration
        sub_problems = decomposition.split("\n")
        exploration_tasks = [
            self.generate(
                instruction=f"""Solve the following sub-problem using appropriate techniques:
                {sub_problem}
                
                Provide detailed reasoning and intermediate results.""",
                context=""
            ) for sub_problem in sub_problems if sub_problem.strip()
        ]
        exploration_results = await asyncio.gather(*exploration_tasks)

        # Step 4: Iterative Refinement
        refinement_tasks = [
            self.revise(
                instruction=f"""Validate and refine the solution for this sub-problem:
                {result}
                
                Ensure correctness, completeness, and clarity.""",
                context=result
            ) for result in exploration_results
        ]
        refined_results = await asyncio.gather(*refinement_tasks)

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize the refined results:
            - Compare solutions for consistency and correctness.
            - Combine complementary insights to construct a unified solution.
            - Present the final answer as an integer between 000 and 999.""",
            contexts_list=refined_results
        )

        return final_solution