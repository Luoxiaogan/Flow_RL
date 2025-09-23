# Workflow ID: hotpotqa_70_0
# Benchmark: hotpotqa
# Data Indices: [417]

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
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities (names, places, organizations) mentioned in the question.
            3. Identify potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Identify bridge entities and reasoning paths
        bridge_entities_task = self.generate(
            instruction=f"""Identify bridge entities connecting documents:
            Question Analysis: {analysis}
            Find shared entities or concepts across documents that can form reasoning chains.""",
            context=analysis
        )
        reasoning_paths_task = self.generate(
            instruction=f"""Construct reasoning chains:
            Question Analysis: {analysis}
            Using extracted entities, build logical chains connecting documents to derive the answer.""",
            context=analysis
        )
        bridge_entities, reasoning_paths = await asyncio.gather(bridge_entities_task, reasoning_paths_task)

        # Step 3: Validation and Refinement - Ensure clarity and correctness
        refined_bridge_entities = await self.revise(
            instruction="Verify and refine identified bridge entities for accuracy.",
            context=bridge_entities
        )
        refined_reasoning_paths = await self.revise(
            instruction="Validate reasoning chains and correct any logical gaps.",
            context=reasoning_paths
        )

        # Step 4: Final Answer Synthesis - Extract and summarize the answer
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract precise answer from reasoning chains:
                Refined Bridge Entities: {refined_bridge_entities}
                Refined Reasoning Paths: {refined_reasoning_paths}
                Focus on extracting exact answer spans from the final document.""",
                context=refined_reasoning_paths
            ),
            self.generate(
                instruction=f"""Summarize supporting facts:
                Refined Bridge Entities: {refined_bridge_entities}
                Refined Reasoning Paths: {refined_reasoning_paths}
                Identify sentences from documents that support the answer.""",
                context=refined_reasoning_paths
            )
        )
        final_answer = await self.ensemble(
            instruction="Select the most accurate and concise answer from candidates.",
            contexts_list=candidate_answers
        )

        # Step 5: Iterative Refinement - Ensure completeness
        refined_final_answer = await self.revise(
            instruction="Ensure the final answer is precise, factual, and supported by evidence.",
            context=final_answer
        )

        return refined_final_answer