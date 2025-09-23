# Workflow ID: hotpotqa_309_0
# Benchmark: hotpotqa
# Data Indices: [445]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type: bridge, comparison, or compositional.
            2. Extract key entities, relationships, and constraints.
            3. Identify relevant documents and sections.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Exploration - Identify reasoning paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Find reasoning paths connecting documents for a bridge question.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Compare properties across documents for a comparison question.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Combine multiple facts for a compositional question.""",
                context=initial_analysis
            )
        )

        # Step 3: Conditional Branching - Adapt based on question type
        question_type = re.search(r"(bridge|comparison|compositional)", initial_analysis, re.IGNORECASE)
        if question_type:
            question_type = question_type.group(0).lower()
            if question_type == "bridge":
                reasoning_chain = reasoning_paths[0]
            elif question_type == "comparison":
                reasoning_chain = reasoning_paths[1]
            else:  # compositional
                reasoning_chain = reasoning_paths[2]
        else:
            reasoning_chain = await self.ensemble(
                instruction="Select the most plausible reasoning chain.",
                contexts_list=reasoning_paths
            )

        # Step 4: Validation Loop - Refine and validate the reasoning chain
        refined_chain = reasoning_chain
        for _ in range(3):  # Limit iterations to avoid excessive latency
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {refined_chain}
                Check for logical consistency, factual accuracy, and completeness.""",
                context=refined_chain
            )
            if "error" in validation.lower() or "incomplete" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain based on validation:
                    {validation}""",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Final Synthesis - Extract and present the precise answer
        final_answer = await self.summarize(
            instruction=f"""Extract the precise answer from the refined reasoning chain:
            {refined_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=refined_chain
        )

        return final_answer