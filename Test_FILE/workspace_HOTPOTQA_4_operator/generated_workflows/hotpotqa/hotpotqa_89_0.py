# Workflow ID: hotpotqa_89_0
# Benchmark: hotpotqa
# Data Indices: [492, 4]

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

        # Phase 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Bridge: Requires connecting shared entities across documents.
            - Comparison: Involves contrasting properties.
            - Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Phase 2: Extract key information from each document
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_tasks = [
            self.generate(
                instruction=f"""Extract key entities, relationships, and facts from this document:
                {doc}""",
                context=""
            )
            for doc in documents if doc.strip()
        ]
        extracted_info = await asyncio.gather(*document_tasks)

        # Phase 3: Identify shared entities and construct reasoning chains
        reasoning_chain = await self.ensemble(
            instruction="""Find shared entities or overlapping concepts across these documents:
            - Highlight entities mentioned in multiple documents.
            - Construct reasoning chains that connect these entities to answer the question.
            Provide a clear explanation of the connections.""",
            contexts_list=extracted_info
        )

        # Phase 4: Extract the precise answer
        answer_extraction = await self.revise(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer to the question:
            {self.problem_text.split("**QUESTION:**")[1].split("**ANSWER:**")[0].strip()}
            Ensure the answer is a short, factual span directly supported by the documents.""",
            context=reasoning_chain
        )

        # Phase 5: Validate and refine the answer
        validation = await self.generate(
            instruction=f"""Validate the answer:
            {answer_extraction}
            
            Check if it aligns with the question and supporting facts. If not, suggest refinements.""",
            context=answer_extraction
        )
        if "error" in validation.lower() or "discrepancy" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                {validation}""",
                context=answer_extraction
            )
            return refined_answer
        else:
            return answer_extraction