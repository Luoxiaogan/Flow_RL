# Workflow ID: hotpotqa_288_0
# Benchmark: hotpotqa
# Data Indices: [486]

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

        # Step 1: Initial Analysis - Classify problem type and extract entities
        analysis = await self.generate(
            instruction="""Classify the problem type (bridge, comparison, compositional) and extract key entities:
            - What is being asked?
            - What are the named entities (people, places, organizations)?
            - Which documents are likely to contain relevant information?
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate reasoning chains for each document
        reasoning_tasks = []
        for doc in range(1, 11):  # Assuming up to 10 documents
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""For Document {doc}, analyze the connection to the extracted entities:
                    - How do the entities relate to the document's content?
                    - What facts support the reasoning chain?
                    - Are there any bridge entities linking this document to others?""",
                    context=analysis
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Step 3: Synthesis - Combine insights from parallel explorations
        synthesis = await self.ensemble(
            instruction="""Synthesize the reasoning chains into a cohesive answer:
            - Identify the most plausible connections between documents.
            - Combine facts to form a complete reasoning chain.
            - Ensure logical coherence and factual accuracy.""",
            contexts_list=reasoning_chains
        )

        # Step 4: Validation and Refinement - Ensure factual correctness and precision
        validation = await self.generate(
            instruction=f"""Validate the synthesized answer:
            - Cross-reference with the original documents.
            - Check for factual accuracy and precision.
            - Identify any missing or conflicting information.""",
            context=synthesis
        )

        refined_answer = await self.revise(
            instruction="Refine the answer for clarity, conciseness, and precision.",
            context=validation
        )

        return refined_answer