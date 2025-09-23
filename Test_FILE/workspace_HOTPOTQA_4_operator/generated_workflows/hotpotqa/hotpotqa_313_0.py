# Workflow ID: hotpotqa_313_0
# Benchmark: hotpotqa
# Data Indices: [22]

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
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Involves comparing properties across documents.
            3. Compositional: Combines multiple facts to derive the answer.
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract key entities and relationships in parallel
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0]
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from the following document:
                {doc}
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ) for doc in documents.split("Document ")[1:]
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build a reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {extracted_entities}
            
            Build a reasoning chain to answer the question:
            {self.problem_text.split("**QUESTION:**")[1].split("**ANSWER:**")[0]}
            Ensure the chain connects facts across at least two documents.""",
            context=question_type
        )

        # Step 4: Validate the reasoning chain iteratively
        for _ in range(3):  # Allow up to 3 iterations for refinement
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {reasoning_chain}
                
                Check for:
                - Logical consistency
                - Factual accuracy
                - Completeness of evidence
                Provide feedback for improvement.""",
                context=question_type
            )
            if "error" in validation.lower():
                reasoning_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain based on the following feedback:
                    {validation}""",
                    context=reasoning_chain
                )
            else:
                break

        # Step 5: Extract the precise answer
        candidate_answers = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain:
                {reasoning_chain}
                
                Ensure the answer is a short, factual span directly supported by the documents.""",
                context=""
            ),
            self.generate(
                instruction=f"""Cross-check the answer with the original documents:
                {documents}
                
                Ensure the answer is factually correct and supported by evidence.""",
                context=reasoning_chain
            )
        )

        # Step 6: Ensemble to select the best-supported answer
        final_answer = await self.ensemble(
            instruction="""Select the best-supported answer based on evidence from different documents.
            Criteria:
            - Factually accurate
            - Directly supported by evidence
            - Concise and precise""",
            contexts_list=candidate_answers
        )

        return final_answer