# Workflow ID: hotpotqa_249_0
# Benchmark: hotpotqa
# Data Indices: [63, 314]

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

        # Step 1: Classify the problem type and identify key components
        classification = await self.generate(
            instruction="""Classify the problem into one of the following types:
            - Bridge: Connects documents through shared entities.
            - Comparison: Compares properties across documents.
            - Compositional: Combines multiple facts to derive an answer.
            Identify the question type and list relevant entities/documents.""",
            context=""
        )

        # Step 2: Extract relevant entities and documents in parallel
        entities_and_documents = await asyncio.gather(
            self.generate(
                instruction=f"""Extract all named entities and relevant documents for the problem.
                Focus on entities that could serve as bridge entities or comparison points.
                Classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Identify documents that contain supporting facts for the problem.
                Classification: {classification}""",
                context=""
            )
        )
        entities = entities_and_documents[0]
        relevant_documents = entities_and_documents[1]

        # Step 3: Build reasoning chains based on problem type
        if "bridge" in classification.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Build a reasoning chain for the bridge question.
                - Identify the bridge entity connecting the documents.
                - Trace the relationship between entities.
                Entities: {entities}
                Relevant Documents: {relevant_documents}""",
                context=classification
            )
        elif "comparison" in classification.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Build a reasoning chain for the comparison question.
                - Extract comparable attributes from the documents.
                - Compare the attributes to determine the answer.
                Entities: {entities}
                Relevant Documents: {relevant_documents}""",
                context=classification
            )
        else:  # Compositional
            reasoning_chain = await self.generate(
                instruction=f"""Build a reasoning chain for the compositional question.
                - Combine multiple facts from the documents.
                - Derive the final answer logically.
                Entities: {entities}
                Relevant Documents: {relevant_documents}""",
                context=classification
            )

        # Step 4: Validate and refine the reasoning chain
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain:
            - Check factual correctness against the documents.
            - Ensure the chain connects supporting facts logically.
            Reasoning Chain: {reasoning_chain}""",
            context=classification
        )
        refined_reasoning = await self.revise(
            instruction=f"""Refine the reasoning chain based on validation feedback.
            Feedback: {validation}""",
            context=reasoning_chain
        )

        # Step 5: Extract the final answer
        answer = await self.generate(
            instruction=f"""Extract the final answer from the refined reasoning chain.
            - Answer must be a short text span or yes/no response.
            - Ensure the answer is factually correct and supported by the documents.
            Refined Reasoning: {refined_reasoning}""",
            context=classification
        )

        # Step 6: Summarize the evidence chain
        evidence_chain = await self.summarize(
            instruction=f"""Summarize the evidence chain supporting the answer.
            - List supporting facts from different documents.
            - Highlight the logical connections between facts.
            Refined Reasoning: {refined_reasoning}""",
            context=answer
        )

        return {
            "answer": answer,
            "evidence_chain": evidence_chain
        }