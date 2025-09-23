# Workflow ID: hotpotqa_188_0
# Benchmark: hotpotqa
# Data Indices: [242]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting documents through shared entities.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Identify potential bridge entities
        entities = await self.generate(
            instruction=f"""Based on the question type ({question_type}), identify potential bridge entities or key concepts:
            - Entities should appear in multiple documents.
            - Include relationships or shared terms.
            Format as a structured list.""",
            context=""
        )

        # Step 3: Explore reasoning chains in parallel
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using entity: {entity}.
                - Connect facts across documents.
                - Ensure logical consistency.
                - Identify supporting evidence.""",
                context=entities
            ) for entity in entities.split("\n") if entity.strip()]
        )

        # Step 4: Validate and refine reasoning chains
        refined_chains = []
        for chain in reasoning_chains:
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                - Check factual correctness.
                - Ensure all steps are supported by evidence.
                - Identify any gaps or inconsistencies.""",
                context=chain
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the reasoning chain to address issues:
                    - Fix gaps or inconsistencies.
                    - Strengthen supporting evidence.""",
                    context=chain
                )
                refined_chains.append(refined)
            else:
                refined_chains.append(chain)

        # Step 5: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Select the most plausible reasoning chain:
            - Prioritize factual correctness.
            - Ensure completeness and logical consistency.""",
            contexts_list=refined_chains
        )

        # Step 6: Extract the final answer
        answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Format as a short text span or yes/no response.
            - Ensure exact match with supporting evidence.""",
            context=best_chain
        )

        return answer