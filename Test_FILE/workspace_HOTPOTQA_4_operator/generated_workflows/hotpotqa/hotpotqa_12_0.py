# Workflow ID: hotpotqa_12_0
# Benchmark: hotpotqa
# Data Indices: [170]

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
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting documents through shared entities (e.g., "What nationality is the director of [movie]?")
            - Comparison: Requires comparing properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional: Requires combining multiple facts to derive the answer
            
            Analyze the question structure and provide the classification along with reasoning.""",
            context=""
        )

        # Step 2: Extract relevant information from documents
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract key entities, relationships, and facts from this document. Focus on information relevant to the question type: {classification}.",
                context=doc
            ) for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document ")[1:]]
        )

        # Step 3: Summarize extracted information
        summarized_info = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the extracted information into a structured format, preserving key entities and relationships.",
                context=summary
            ) for summary in document_summaries]
        )

        # Step 4: Build reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"Using the summarized information, construct a reasoning chain to answer the question. Focus on the question type: {classification}.",
                context="\n".join(summarized_info)
            ) for _ in range(2)]  # Generate multiple chains for robustness
        )

        # Step 5: Validate and refine reasoning chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine the reasoning chain. Ensure logical consistency and completeness.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 6: Select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="Evaluate the reasoning chains and select the most plausible one. Consider logical consistency, completeness, and alignment with the question type.",
            contexts_list=refined_chains
        )

        # Step 7: Extract the precise answer
        answer = await self.generate(
            instruction="Extract the precise answer from the reasoning chain. Provide exact text spans or yes/no responses as required.",
            context=best_chain
        )

        # Step 8: Verify the answer
        verified_answer = await self.revise(
            instruction="Verify the extracted answer against the original documents. Ensure factual correctness and direct support.",
            context=answer
        )

        return verified_answer