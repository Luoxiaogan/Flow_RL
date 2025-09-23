# Workflow ID: gsm8k_125_0
# Benchmark: gsm8k
# Data Indices: [123, 268]

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
        
        # Phase 1: Initial Analysis
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        classification = await self.generate(
            instruction=f"""Classify this problem based on extracted entities:
            {entities}
            
            Categories:
            - Rate (distance/speed/time)
            - Distribution (sharing/dividing quantities)
            - Proportion (percentages/ratios)
            - Multi-entity (tracking multiple objects/people)""",
            context=entities
        )
        
        # Phase 2: Sub-problem Generation
        sub_problems = await self.generate(
            instruction=f"""Based on classification:
            {classification}
            
            Define sub-problems to solve sequentially. Include:
            - Known values
            - Unknowns to calculate
            - Relationships between them""",
            context=entities
        )
        
        # Phase 3: Sequential Solution
        sub_problem_list = sub_problems.split("\n")
        intermediate_results = []
        
        for sub_problem in sub_problem_list:
            solution = await self.generate(
                instruction=f"""Solve this sub-problem:
                {sub_problem}
                
                Show all steps and intermediate results.""",
                context="\n".join(intermediate_results)
            )
            validated = await self.revise(
                instruction=f"""Validate this solution:
                {solution}
                
                Check for errors and refine if necessary.""",
                context=solution
            )
            intermediate_results.append(validated)
        
        # Phase 4: Final Synthesis
        final_answer = await self.ensemble(
            instruction=f"""Synthesize all intermediate results into the final answer:
            Intermediate Results:
            {' '.join(intermediate_results)}
            
            Ensure numerical precision and coherence.""",
            contexts_list=intermediate_results
        )
        
        return await self.summarize(
            instruction="Condense the final answer into a single numerical value.",
            context=final_answer
        )