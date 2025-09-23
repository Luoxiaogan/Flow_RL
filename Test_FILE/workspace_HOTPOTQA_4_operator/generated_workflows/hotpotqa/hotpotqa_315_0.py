# Workflow ID: hotpotqa_315_0
# Benchmark: hotpotqa
# Data Indices: [394]

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
            instruction="""Classify the problem into one of the following types:
            - Bridge Question: Requires connecting entities across documents
            - Comparison Question: Involves comparing properties or attributes
            - Compositional Question: Needs combining multiple facts to derive an answer
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents in parallel
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities, relationships, and key sentences from the following document:
                {doc}
                Format the output as a structured list with categories: Entities, Relationships, Key Sentences.""",
                context=""
            )
            for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")
            if doc.strip()
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Identify bridge entities and construct reasoning chains
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {extracted_entities}
            
            Identify bridge entities that connect multiple documents and construct a reasoning chain to answer the question:
            {self.problem_text.split("**QUESTION:**")[1].split("**ANSWER:")[0].strip()}
            Provide a clear chain of reasoning with supporting facts.""",
            context=""
        )

        # Step 4: Validate and refine the reasoning chain
        refined_chain = await self.revise(
            instruction="""Ensure the reasoning chain is logically sound and factually accurate:
            - Verify that each step follows from the previous one
            - Check that all supporting facts are explicitly stated in the documents
            - Correct any inconsistencies or gaps""",
            context=reasoning_chain
        )

        # Step 5: Extract candidate answers and select the best one
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the final answer from the refined reasoning chain:
                {refined_chain}
                Ensure the answer is precise and directly addresses the question.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose an alternative answer by exploring a different reasoning path:
                {refined_chain}
                Ensure the alternative is plausible and supported by evidence.""",
                context=""
            )
        )
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and well-supported answer:
            - Compare the candidate answers based on factual correctness
            - Evaluate the strength of their supporting evidence
            - Choose the best option""",
            contexts_list=candidate_answers
        )

        return final_answer