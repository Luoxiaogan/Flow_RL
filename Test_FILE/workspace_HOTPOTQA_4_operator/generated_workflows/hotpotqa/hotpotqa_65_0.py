# Workflow ID: hotpotqa_65_0
# Benchmark: hotpotqa
# Data Indices: [46]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify the main subject and target of the question
            - List all named entities (people, places, concepts) mentioned in the question
            - Note any explicit relationships or constraints""",
            context=""
        )

        # Step 2: Parallel Entity and Relationship Extraction
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_sections = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        
        async def process_document(doc):
            return await self.generate(
                instruction=f"""Extract all entities and relationships from the following document:
                {doc}
                Focus on entities relevant to the question and their connections.""",
                context=initial_analysis
            )
        
        extracted_data = await asyncio.gather(*[process_document(doc) for doc in doc_sections])

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="""Construct the most coherent reasoning chain:
            - Connect entities across documents using shared relationships
            - Ensure each step is factually supported by the text
            - Prioritize chains that directly answer the question""",
            contexts_list=extracted_data
        )

        # Step 4: Iterative Refinement
        refined_chain = reasoning_chain
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the reasoning chain:
                {refined_chain}
                Identify any gaps, inconsistencies, or unsupported claims.""",
                context=initial_analysis
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"""Refine the reasoning chain to address issues:
                    Issues: {validation}
                    Ensure the chain remains coherent and factually supported.""",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the documents:
            Reasoning Chain: {refined_chain}
            Ensure the answer is directly supported by the text and matches the question format.""",
            context=initial_analysis
        )

        return answer