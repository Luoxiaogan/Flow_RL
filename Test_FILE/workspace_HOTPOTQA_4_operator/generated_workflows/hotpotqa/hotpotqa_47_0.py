# Workflow ID: hotpotqa_47_0
# Benchmark: hotpotqa
# Data Indices: [267, 345]

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
        import re

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting information through shared entities.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification with justification.""",
            context=""
        )

        # Step 2: Parallel document analysis
        documents = re.findall(r"Document \d+:.*?(?=\n\nDocument|\n\nQUESTION)", self.problem_text, re.DOTALL)
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract key entities, relationships, and facts from the following document:
                {doc}
                Focus on information relevant to the question type: {question_type}.""",
                context=""
            ) for doc in documents]
        )

        # Step 3: Build reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information from all documents:
            {document_analyses}
            
            Identify bridge entities and construct a reasoning chain that connects the documents.
            Ensure the chain leads logically to the answer.""",
            context=""
        )

        # Step 4: Extract and validate answer
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract the precise answer from the following document analysis:
                {analysis}
                Ensure the answer is directly supported by the reasoning chain: {reasoning_chain}.""",
                context=""
            ) for analysis in document_analyses]
        )
        final_answer = await self.ensemble(
            instruction=f"""Select the most accurate and factually supported answer from the candidates:
            {candidate_answers}
            Validate against the reasoning chain: {reasoning_chain}.""",
            contexts_list=candidate_answers
        )

        # Step 5: Iterative refinement (if needed)
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the final answer:
                {final_answer}
                
                Check if it is factually correct and fully supported by the reasoning chain: {reasoning_chain}.
                If not, suggest improvements.""",
                context=""
            )
            if "error" in validation.lower() or "improve" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"""Refine the answer based on validation feedback:
                    {validation}""",
                    context=final_answer
                )
            else:
                break

        return final_answer