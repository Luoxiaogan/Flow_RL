# Workflow ID: hotpotqa_218_0
# Benchmark: hotpotqa
# Data Indices: [23]

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

        # Step 1: Classify the problem type
        problem_type = await self.generate(
            instruction="""Classify the problem:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify key entities and relationships involved.
            - Suggest potential reasoning chains.
            Provide a structured classification.""",
            context=""
        )

        # Step 2: Extract information from documents in parallel
        documents = self.problem_text.split("Document ")[1:]  # Split by document
        extracted_info = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract relevant information from this document:
                - Key entities (e.g., band names, album titles)
                - Numerical data or properties (e.g., number of members, founding year)
                - Relationships between entities
                Format as structured list.""",
                context=doc
            ) for doc in documents]
        )

        # Step 3: Refine extracted information
        refined_info = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the extracted information:
                - Ensure accuracy and completeness
                - Resolve ambiguities
                - Highlight connections to other documents""",
                context=info
            ) for info in extracted_info]
        )

        # Step 4: Synthesize findings and derive the answer
        synthesis = await self.ensemble(
            instruction=f"""Synthesize the refined information:
            - Combine facts from different documents
            - Resolve conflicts or ambiguities
            - Derive the final answer based on the problem type
            Problem Type: {problem_type}
            Provide the exact answer span and supporting evidence.""",
            contexts_list=refined_info
        )

        # Step 5: Return the final answer
        return synthesis