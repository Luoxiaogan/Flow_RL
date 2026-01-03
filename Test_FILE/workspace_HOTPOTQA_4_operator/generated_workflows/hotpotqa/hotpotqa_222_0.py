# Workflow ID: hotpotqa_222_0
# Benchmark: hotpotqa
# Data Indices: [131]

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
            instruction="""Classify the problem into one of the following categories:
            - Bridge: Requires connecting documents through shared entities.
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts to derive an answer.
            Provide a clear classification with justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_and_relationships = await self.generate(
            instruction=f"""Extract key entities and relationships from the documents:
            - Named entities (people, places, organizations).
            - Relationships between entities (e.g., 'founded by', 'located in').
            - Temporal or ordinal data for comparison questions.
            Problem Type: {problem_type}""",
            context=""
        )

        # Step 3: Generate hypotheses in parallel
        hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate hypotheses for bridge questions:
                Identify potential shared entities and evaluate their relevance.
                Entities and Relationships: {entities_and_relationships}""",
                context=entities_and_relationships
            ),
            self.generate(
                instruction=f"""Generate hypotheses for comparison questions:
                Extract comparable properties and assess their validity.
                Entities and Relationships: {entities_and_relationships}""",
                context=entities_and_relationships
            ),
            self.generate(
                instruction=f"""Generate hypotheses for compositional questions:
                Combine facts from different documents to form candidate answers.
                Entities and Relationships: {entities_and_relationships}""",
                context=entities_and_relationships
            )
        )

        # Step 4: Synthesize evidence
        evidence_synthesis = await self.ensemble(
            instruction="""Synthesize evidence from the documents to validate hypotheses:
            - Trace reasoning chains across documents.
            - Verify factual accuracy of connections.
            - Extract precise answer spans from the text.""",
            contexts_list=hypotheses
        )

        # Step 5: Iterative refinement (if needed)
        refined_answer = await self.revise(
            instruction="""Refine the answer if necessary:
            - Revisit entity and relationship extraction for overlooked connections.
            - Generate additional hypotheses based on new insights.
            - Re-evaluate reasoning chains for completeness.
            Current Evidence Synthesis: {evidence_synthesis}""",
            context=evidence_synthesis
        )

        # Step 6: Extract final answer
        final_answer = await self.generate(
            instruction=f"""Extract the precise answer from the validated reasoning chain:
            - Ensure the answer matches the expected format (short text span or yes/no response).
            - Return supporting facts that justify the answer.
            Refined Answer: {refined_answer}""",
            context=refined_answer
        )

        return final_answer