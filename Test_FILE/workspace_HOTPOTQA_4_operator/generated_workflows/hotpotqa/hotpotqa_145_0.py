# Workflow ID: hotpotqa_145_0
# Benchmark: hotpotqa
# Data Indices: [254, 73]

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

        # Phase 1: Problem Analysis and Question Classification
        problem_analysis = await self.generate(
            instruction="""Analyze the question and classify it into one of the following types:
            1. Bridge Question: Connects two or more documents through shared entities.
            2. Comparison Question: Compares properties across documents.
            3. Compositional Question: Combines multiple facts to derive an answer.
            Provide the classification along with a brief explanation.""",
            context=""
        )

        # Phase 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and key facts from the context documents.
            Format as a structured list:
            - Entities: [names, types]
            - Relationships: [connections between entities]
            - Key Facts: [important sentences or phrases]""",
            context=problem_analysis
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain based on the following information:
                Question Type: {problem_analysis}
                Extracted Entities and Relationships: {entities}
                
                Follow these steps:
                1. Identify bridge entities connecting documents.
                2. Trace the reasoning path across documents.
                3. Ensure the chain is supported by explicit evidence.""",
                context=entities
            ) for _ in range(3)]  # Generate 3 candidate chains
        )

        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the best-supported one.
            Criteria:
            - Strength of evidence
            - Coherence of reasoning
            - Relevance to the question""",
            contexts_list=reasoning_chains
        )

        # Phase 4: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain.
            Ensure the answer is a short text span or yes/no response.
            Reasoning Chain: {best_chain}""",
            context=best_chain
        )

        # Phase 5: Iterative Refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the answer against the supporting facts.
            Is the answer factually correct and supported by explicit evidence?
            If not, identify the issues.""",
            context=answer
        )

        if "error" in validation.lower() or "incomplete" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on the following feedback:
                {validation}
                
                Ensure the revised answer is precise and supported by evidence.""",
                context=answer
            )
            return refined_answer
        else:
            return answer