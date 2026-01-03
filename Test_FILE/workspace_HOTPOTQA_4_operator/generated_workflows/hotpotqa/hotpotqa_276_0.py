# Workflow ID: hotpotqa_276_0
# Benchmark: hotpotqa
# Data Indices: [194]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the question:
            - Identify the type: bridge, comparison, or compositional
            - Extract key entities and relationships
            - Determine the reasoning strategy required
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Document Analysis (Parallel Processing)
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract key information from this document:
                - Entities and their roles
                - Relationships and facts
                - Potential connections to other documents
                Document: {doc}""",
                context=""
            ) for doc in documents.split("Document ")[1:]]
        )

        # Summarize each document's key points
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the extracted information into key points.",
                context=summary
            ) for summary in doc_summaries]
        )

        # Phase 3: Cross-Document Connection
        connections = await self.ensemble(
            instruction="""Identify shared entities or concepts across documents:
            - Find overlapping entities or relationships
            - Determine how they connect to form a reasoning chain
            Provide a synthesis of connections.""",
            contexts_list=summaries
        )

        reasoning_chain = await self.generate(
            instruction=f"""Using the identified connections:
            {connections}
            
            Construct a logical reasoning chain that leads to the answer.
            - Start with the question's requirements
            - Follow the chain of connections across documents
            - End with the document containing the final answer""",
            context=connections
        )

        # Phase 4: Answer Synthesis
        answer_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from this document:
                - Focus on the final step of the reasoning chain
                - Ensure the answer matches the question's requirements
                Document: {doc}""",
                context=reasoning_chain
            ) for doc in documents.split("Document ")[1:]]
        )

        final_answer = await self.ensemble(
            instruction="""Select the best answer based on supporting evidence:
            - Factually correct
            - Directly addresses the question
            - Supported by the reasoning chain""",
            contexts_list=answer_candidates
        )

        # Phase 5: Validation and Refinement
        validated_answer = await self.revise(
            instruction="""Validate the answer:
            - Check factual accuracy
            - Ensure alignment with the reasoning chain
            - Refine if necessary""",
            context=final_answer
        )

        return validated_answer