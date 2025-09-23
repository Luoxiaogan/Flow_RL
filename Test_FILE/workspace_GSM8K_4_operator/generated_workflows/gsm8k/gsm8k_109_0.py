# Workflow ID: gsm8k_109_0
# Benchmark: gsm8k
# Data Indices: [9, 74]

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
        
        # Initial Analysis: Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships.
            Classify the problem type (e.g., rate, proportion, distribution).
            Identify what the question asks for.
            Format as structured list with categories:
            - Numbers: [values and what they represent]
            - Units: [units and their context]
            - Relationships: [how numbers relate to each other]
            - Question: [what is being asked]""",
            context=""
        )
        
        # Parallel Exploration: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted structure:
                {initial_analysis}
                
                Develop solution path focusing on sequential operations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the extracted structure:
                {initial_analysis}
                
                Develop solution path focusing on rate relationships.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the extracted structure:
                {initial_analysis}
                
                Develop solution path focusing on proportions and scaling.""",
                context=initial_analysis
            )
        )
        
        # Validation and Refinement: Validate each path and refine as needed
        refined_paths = []
        for path in solution_paths:
            validation = await self.generate(
                instruction=f"Validate the following solution path: {path}",
                context=path
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues identified in validation: {validation}",
                    context=path
                )
                refined_paths.append(refined)
            else:
                refined_paths.append(path)
        
        # Synthesis: Combine insights from different paths
        synthesis = await self.ensemble(
            instruction="Synthesize all solution paths into a unified understanding.",
            contexts_list=refined_paths
        )
        
        # Final Answer Extraction: Ensure the final answer is precise
        final_answer = await self.generate(
            instruction=f"""From the synthesized solution:
            {synthesis}
            
            Extract the final numerical answer, ensuring it is precise and correctly formatted.""",
            context=synthesis
        )
        
        return final_answer