# Workflow ID: hotpotqa_104_0
# Benchmark: hotpotqa
# Data Indices: [190, 383]

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

        # Step 1: Initial Analysis - Classify the question type
        initial_analysis = await self.generate(
            instruction="""Classify the question type:
            1. Identify if it's a bridge, comparison, or compositional question.
            2. Extract key entities and relationships mentioned in the question.
            3. Provide a structured classification with reasoning.""",
            context=""
        )

        # Step 2: Entity and Fact Extraction - Parallel exploration
        entities_and_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract entities and facts from Document {i+1}:
                - Focus on entities mentioned in the question ({initial_analysis})
                - Identify relationships and supporting facts""",
                context=""
            ) for i in range(10)]  # Assuming up to 10 documents
        )

        # Step 3: Reasoning Chain Construction - Sequential and parallel processing
        reasoning_chains = []
        for i, doc_entities in enumerate(entities_and_facts):
            chain = await self.generate(
                instruction=f"""Using entities and facts from Document {i+1}:
                - Build logical connections with other documents
                - Focus on shared entities or properties""",
                context=doc_entities
            )
            reasoning_chains.append(chain)

        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity and add missing connections",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 4: Answer Extraction and Validation - Ensemble selection
        summary = await self.summarize(
            instruction="Condense the reasoning chains into a concise summary",
            context="\n".join(refined_chains)
        )

        answer_candidates = await asyncio.gather(
            self.generate(instruction="Extract the final answer from the summary", context=summary),
            self.generate(instruction="Provide an alternative answer if possible", context=summary)
        )

        final_answer = await self.ensemble(
            instruction="Select the most accurate and factual answer",
            contexts_list=answer_candidates
        )

        return final_answer