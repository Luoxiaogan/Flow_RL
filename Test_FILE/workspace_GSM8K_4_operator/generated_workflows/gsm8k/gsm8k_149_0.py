# Workflow ID: gsm8k_149_0
# Benchmark: gsm8k
# Data Indices: [25, 225]

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
        analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships:
            - Identify what is being asked
            - List all given numbers and their context
            - Highlight dependencies and constraints""",
            context=""
        )
        
        # Step 2: Classify problem type
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Classify the problem type:
            - Sequential operations (e.g., multiplication followed by division)
            - Rate problems (e.g., distance/speed/time)
            - Distribution problems (e.g., dividing quantities)
            - Proportions (e.g., percentages, fractions)
            - Multi-entity tracking (e.g., different people/objects)
            
            Provide a clear strategy for solving.""",
            context=analysis
        )
        
        # Step 3: Execute parallel computations (if applicable)
        parallel_tasks = []
        if "parallel" in strategy.lower():
            tasks = await self.generate(
                instruction=f"""Identify independent calculations from:
                {strategy}
                
                Generate tasks for parallel execution.""",
                context=strategy
            )
            parallel_tasks = [self.generate(instruction=task, context="") for task in tasks.split("\n")]
        
        parallel_results = await asyncio.gather(*parallel_tasks) if parallel_tasks else []
        
        # Step 4: Sequential execution
        sequential_results = []
        current_context = analysis
        for i in range(8):  # Maximum 8 steps
            step = await self.generate(
                instruction=f"""Execute step {i+1} based on:
                {current_context}
                
                Show calculations and intermediate results.""",
                context=current_context
            )
            validated_step = await self.revise(
                instruction=f"""Validate step {i+1}:
                {step}
                
                Check for errors and provide corrections if needed.""",
                context=step
            )
            sequential_results.append(validated_step)
            current_context = validated_step
            
            if "final answer" in validated_step.lower():
                break
        
        # Step 5: Combine results
        final_result = await self.ensemble(
            instruction="""Synthesize all results into a final answer:
            - Ensure coherence and consistency
            - Present the final numerical value""",
            contexts_list=[*parallel_results, *sequential_results]
        )
        
        return final_result