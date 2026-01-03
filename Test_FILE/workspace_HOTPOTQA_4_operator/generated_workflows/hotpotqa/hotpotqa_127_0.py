# Workflow ID: hotpotqa_127_0
# Benchmark: hotpotqa
# Data Indices: [342]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify the main subject(s) of the question
            - Determine the type of relationship being asked about
            - Extract named entities, numbers, and relationships from the question""",
            context=""
        )

        # Step 2: Parallel Exploration - Analyze multiple reasoning paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Analyze potential bridge entities and their connections:
                {initial_analysis}
                
                Focus on entities that appear in multiple documents and could serve as bridges.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Analyze potential comparison points:
                {initial_analysis}
                
                Focus on properties or attributes that can be compared across documents.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Analyze potential compositional facts:
                {initial_analysis}
                
                Focus on combining multiple facts to derive the answer.""",
                context=initial_analysis
            )
        )

        # Step 3: Synthesis - Select the most promising reasoning chain
        synthesis = await self.ensemble(
            instruction="""Evaluate the reasoning paths and select the most promising one:
            - Consider factual accuracy
            - Ensure logical coherence
            - Prioritize paths supported by multiple documents""",
            contexts_list=reasoning_paths
        )

        # Step 4: Iterative Refinement - Refine the selected reasoning chain
        refined_chain = synthesis
        for _ in range(3):  # Allow up to 3 iterations
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {refined_chain}
                
                Check for logical gaps, missing details, or factual inaccuracies.""",
                context=refined_chain
            )
            if "error" in validation.lower() or "missing" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain based on validation feedback:
                    {validation}""",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Extract Precise Answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the refined reasoning chain:
            {refined_chain}
            
            Ensure the answer is a short, factual span directly from the text.""",
            context=refined_chain
        )

        return answer