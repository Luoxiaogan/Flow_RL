# Workflow ID: hotpotqa_118_0
# Benchmark: hotpotqa
# Data Indices: [326, 265]

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

        # Step 1: Initial Analysis - Classify question and extract entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract:
            - Key entities (people, places, dates, etc.)
            - Relationships between entities
            - Potential bridge entities connecting documents
            Format the output as structured JSON.""",
            context=""
        )

        # Step 2: Parallel Document Processing - Extract relevant information
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_chunks = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        parallel_tasks = [
            self.generate(
                instruction=f"""Extract all relevant information from this document:
                - Entities mentioned
                - Key facts and relationships
                - Potential connections to other documents""",
                context=doc
            ) for doc in doc_chunks
        ]
        extracted_info = await asyncio.gather(*parallel_tasks)

        # Step 3: Merge Extracted Information - Build unified knowledge base
        merged_knowledge = await self.ensemble(
            instruction="""Merge the extracted information into a unified knowledge base:
            - Combine overlapping entities and facts
            - Identify cross-document connections
            - Highlight potential reasoning paths""",
            contexts_list=extracted_info
        )

        # Step 4: Reasoning Chain Construction - Connect entities across documents
        reasoning_chain = await self.generate(
            instruction=f"""Using the merged knowledge base:
            {merged_knowledge}
            
            Construct explicit reasoning chains to answer the question:
            - Follow logical connections between entities
            - Ensure each step is supported by evidence
            - Provide intermediate conclusions""",
            context=initial_analysis
        )
        refined_chain = await self.revise(
            instruction="""Critique and refine the reasoning chain:
            - Check for logical consistency
            - Add missing details
            - Resolve ambiguities""",
            context=reasoning_chain
        )

        # Step 5: Answer Extraction and Validation - Finalize the answer
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the final answer from the reasoning chain:
                {refined_chain}
                
                Ensure the answer is:
                - Factually correct
                - Directly supported by the documents
                - Formatted as a short text span or yes/no response""",
                context=""
            ),
            self.generate(
                instruction=f"""Validate the reasoning chain against the documents:
                {documents}
                
                Identify any discrepancies or unsupported claims""",
                context=refined_chain
            )
        )
        final_answer = await self.ensemble(
            instruction="""Select the most accurate answer:
            - Compare candidate answers
            - Prioritize answers with stronger evidence
            - Flag any unresolved discrepancies""",
            contexts_list=answer_candidates
        )

        return final_answer