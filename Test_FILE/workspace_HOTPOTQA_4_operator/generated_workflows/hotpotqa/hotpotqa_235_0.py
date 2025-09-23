# Workflow ID: hotpotqa_235_0
# Benchmark: hotpotqa
# Data Indices: [87]

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

        # Step 1: Classify the question and extract key entities
        classification = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting documents through shared entities.
            2. Comparison Question: Requires comparing properties across documents.
            3. Compositional Question: Requires combining multiple facts to derive the answer.
            Extract key entities and relationships mentioned in the question.""",
            context=""
        )

        # Step 2: Extract entities and relationships from context documents
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
            )
            for doc in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document")
            if doc.strip()
        ]
        entities_list = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build reasoning chain by connecting entities across documents
        reasoning_chain = await self.ensemble(
            instruction="""Evaluate multiple candidate paths to connect entities across documents:
            - Identify shared entities between documents.
            - Construct reasoning chains that lead to the answer.
            Select the most plausible chain based on supporting evidence.""",
            contexts_list=entities_list
        )

        # Step 4: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            Extract the precise answer from the relevant document. Ensure the answer is factually correct and directly supported by the context documents.""",
            context=reasoning_chain
        )

        validation = await self.revise(
            instruction="""Validate the answer:
            - Check if it is consistent with the reasoning chain.
            - Verify if it directly answers the question.
            - Ensure it is factually correct based on the context documents.""",
            context=answer
        )

        # Step 5: Iterative refinement if needed
        if "error" in validation.lower() or "inconsistent" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                {validation}""",
                context=answer
            )
            return refined_answer

        return answer