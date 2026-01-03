# Workflow ID: hotpotqa_166_0
# Benchmark: hotpotqa
# Data Indices: [228]

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

        # Step 1: Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            - Is the question a bridge, comparison, or compositional type?
            - What are the main entities mentioned in the question?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Document Analysis
        document_texts = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_texts = [f"Document{doc}" for doc in document_texts if doc.strip()]
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all entities, relationships, and facts from this document:
                - Focus on connections between entities.
                - Highlight facts relevant to the question.""",
                context=doc
            ) for doc in document_texts]
        )

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify entities or concepts that appear in multiple documents:
            - Rank them by relevance to the question.
            - Highlight entities that could serve as bridges for multi-hop reasoning.""",
            contexts_list=document_analyses
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain by connecting bridge entities across documents:
            - Start with the entities extracted from the question.
            - Follow connections through the identified bridge entities.
            - End with the document containing the final answer.""",
            context=bridge_entities
        )

        # Step 5: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the exact answer span from the final document in the reasoning chain:
            - Ensure it directly answers the question.
            - Validate against the identified facts.""",
            context=reasoning_chain
        )

        # Step 6: Iterative Refinement
        refined_answer = await self.revise(
            instruction="""Review the reasoning chain and answer for completeness and accuracy:
            - Add missing details or clarify ambiguities.
            - Ensure factual correctness and precision.""",
            context=answer
        )

        return refined_answer