# Workflow ID: hotpotqa_85_0
# Benchmark: hotpotqa
# Data Indices: [261, 272]

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
        question_type_analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (comparing properties across documents)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification with reasoning.""",
            context=""
        )
        
        # Step 2: Extract named entities and identify bridge entities
        entities_extraction = await self.generate(
            instruction=f"""Extract all named entities from the question and context documents.
            Then identify potential bridge entities that connect different documents.
            Question Type Analysis: {question_type_analysis}""",
            context=""
        )
        
        # Step 3: Build reasoning chains
        reasoning_chains_tasks = []
        for entity in entities_extraction.split('\n'):
            reasoning_chains_tasks.append(
                self.generate(
                    instruction=f"""Build a reasoning chain starting from entity: {entity}.
                    Trace logical connections across documents, providing supporting facts for each link.""",
                    context=entities_extraction
                )
            )
        reasoning_chains = await asyncio.gather(*reasoning_chains_tasks)
        
        # Step 4: Revise and refine reasoning chains
        refined_chains_tasks = []
        for chain in reasoning_chains:
            refined_chains_tasks.append(
                self.revise(
                    instruction=f"""Critique and refine the reasoning chain:
                    Ensure logical consistency and factual accuracy.
                    Original Chain: {chain}""",
                    context=chain
                )
            )
        refined_chains = await asyncio.gather(*refined_chains_tasks)
        
        # Step 5: Ensemble to select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most coherent and factually accurate one.
            Consider completeness, logical flow, and supporting evidence.""",
            contexts_list=refined_chains
        )
        
        # Step 6: Extract precise answer
        precise_answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain.
            Ensure it is a short text span or yes/no response.
            Best Reasoning Chain: {best_chain}""",
            context=best_chain
        )
        
        # Step 7: Summarize the final answer and supporting facts
        final_summary = await self.summarize(
            instruction=f"""Summarize the final answer and supporting facts.
            Include the precise answer and key supporting evidence.
            Precise Answer: {precise_answer}
            Best Reasoning Chain: {best_chain}""",
            context=precise_answer
        )
        
        return final_summary