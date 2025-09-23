# Workflow ID: hotpotqa_287_0
# Benchmark: hotpotqa
# Data Indices: [14, 42]

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
        question_analysis = await self.generate(
            instruction="""Classify the question type:
            - Bridge: Requires connecting entities across documents.
            - Comparison: Involves comparing properties.
            - Compositional: Combines multiple facts.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities and relationships:
            - Entities: People, places, organizations, etc.
            - Relationships: Subject-predicate-object triples.
            From both the question and the documents.
            Context: {question_analysis}""",
            context=""
        )

        # Step 3: Match entities across documents and construct reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct reasoning chains using the following entities:
                {entities}
                Identify connections between documents and explain the reasoning.""",
                context=doc
            ) for doc in ["Document 1", "Document 2", "Document 3"]]  # Dynamically adjust for N documents
        )

        # Step 4: Select the best reasoning chain
        selected_chain = await self.ensemble(
            instruction="""Select the most plausible reasoning chain:
            - Relevance to the question.
            - Logical coherence.
            - Evidence support.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the precise answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the final document:
            Reasoning chain: {selected_chain}
            Ensure the answer is an exact span of text and factually correct.""",
            context=""
        )

        # Step 6: Validate and refine the answer
        refined_answer = await self.revise(
            instruction="""Validate and refine the answer:
            - Cross-check with the reasoning chain.
            - Ensure factual accuracy.
            - Format appropriately.""",
            context=answer_extraction
        )

        return refined_answer