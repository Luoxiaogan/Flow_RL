# Workflow ID: hotpotqa_334_0
# Benchmark: hotpotqa
# Data Indices: [184, 198]

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
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities, relationships, and relevant documents.
            3. Highlight potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Build reasoning chains
        reasoning_tasks = []
        for i in range(3):  # Limit to 3 parallel tasks for efficiency
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Using the initial analysis:
                    {initial_analysis}
                    
                    Explore reasoning chain {i+1}:
                    - Connect documents through shared entities.
                    - Build explicit reasoning steps.
                    - Identify supporting facts.""",
                    context=initial_analysis
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Step 3: Synthesis and Refinement - Merge insights and refine
        synthesized_chain = await self.ensemble(
            instruction="""Synthesize reasoning chains:
            - Evaluate completeness and coherence.
            - Select the most robust chain.
            - Highlight any gaps or ambiguities.""",
            contexts_list=reasoning_chains
        )

        refined_chain = await self.revise(
            instruction="""Refine the reasoning chain:
            - Address gaps or ambiguities.
            - Ensure logical flow and factual accuracy.
            - Prepare for final answer extraction.""",
            context=synthesized_chain
        )

        # Step 4: Final Answer Extraction - Extract and validate answer
        final_answer = await self.generate(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the precise answer:
            - Identify the exact answer span from the final document.
            - Ensure alignment with the evidence chain.""",
            context=refined_chain
        )

        validated_answer = await self.revise(
            instruction="""Validate the answer:
            - Check factual correctness.
            - Ensure precision and clarity.
            - Confirm alignment with supporting facts.""",
            context=final_answer
        )

        return validated_answer