# Workflow ID: hotpotqa_16_0
# Benchmark: hotpotqa
# Data Indices: [305]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        analysis = await self.generate(
            instruction="""Analyze the question to determine its type and extract key entities:
            - Is it a bridge question, comparison question, or another type?
            - Identify all named entities (people, places, dates, etc.) mentioned in the question.
            - Highlight relationships or constraints implied by the question.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Document Processing - Extract relevant information from each document
        documents = re.findall(r"Document \d+:.*?(?=\n\n|\Z)", self.problem_text, re.DOTALL)
        async def process_document(doc):
            return await self.generate(
                instruction=f"""Extract sentences or phrases from this document that relate to the entities or constraints identified in the analysis:
                {analysis}
                
                Document Content:
                {doc}""",
                context=""
            )
        document_extractions = await asyncio.gather(*[process_document(doc) for doc in documents])

        # Step 3: Reasoning Chain Construction - Identify bridge entities and synthesize reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize the extracted information into a coherent reasoning chain:
            - Identify bridge entities that connect different documents.
            - Construct a logical sequence that leads from the starting entity to the target entity.
            - Ensure each step is supported by evidence from the documents.
            Provide a detailed explanation of the reasoning chain.""",
            contexts_list=document_extractions
        )

        # Step 4: Answer Extraction and Validation - Extract precise answer and validate
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the final document. Ensure the answer is:
            - Factually accurate based on the documents.
            - Directly supported by the text.
            - Consistent with the question constraints.
            Provide the exact answer span.""",
            context=reasoning_chain
        )

        validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Cross-reference with the original documents.
            - Check for consistency with the reasoning chain.
            - Ensure the answer satisfies the question constraints.
            If necessary, suggest refinements.""",
            context=answer_extraction
        )

        # Step 5: Final Output - Return the validated answer
        final_answer = await self.summarize(
            instruction="Condense the validated answer into a concise, final response.",
            context=validation
        )

        return final_answer