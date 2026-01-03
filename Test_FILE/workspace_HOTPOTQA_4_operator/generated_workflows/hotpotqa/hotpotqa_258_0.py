# Workflow ID: hotpotqa_258_0
# Benchmark: hotpotqa
# Data Indices: [196]

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
            1. Bridge Question: Requires connecting documents through shared entities.
            2. Comparison Question: Requires comparing properties across documents.
            3. Compositional Question: Requires combining multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        document_texts = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, numbers, and relationships from the following document:
                {doc}
                Format as a structured list with categories:
                - Entities: [names and roles]
                - Relationships: [connections between entities]""",
                context=""
            )
            for doc in document_texts
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build reasoning chains
        reasoning_chains = await self.ensemble(
            instruction=f"""Using the extracted entities and relationships:
            {extracted_entities}
            
            Construct reasoning chains that connect the information across documents to answer the question:
            {question_type}
            Evaluate multiple chains and select the most plausible one.""",
            contexts_list=extracted_entities
        )

        # Step 4: Extract and validate the answer
        answer_extraction = await self.summarize(
            instruction=f"""From the reasoning chain:
            {reasoning_chains}
            
            Extract the precise answer to the question in the required format (short text spans or yes/no).""",
            context=reasoning_chains
        )

        answer_validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Ensure it is factually correct, supported by the documents, and adheres to the required format.""",
            context=answer_extraction
        )

        # Step 5: Iterative refinement (if necessary)
        final_answer = answer_validation
        for _ in range(2):  # Allow up to 2 refinement iterations
            if "error" in final_answer.lower():
                refined_answer = await self.revise(
                    instruction=f"""Refine the answer to address the following issues:
                    {final_answer}""",
                    context=final_answer
                )
                final_answer = refined_answer
            else:
                break

        return final_answer