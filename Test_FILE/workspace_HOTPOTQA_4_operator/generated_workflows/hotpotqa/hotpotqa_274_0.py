# Workflow ID: hotpotqa_274_0
# Benchmark: hotpotqa
# Data Indices: [483, 357]

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
            instruction="""Analyze the problem to determine its type and extract key entities:
            - Is this a bridge, comparison, or compositional question?
            - Identify all named entities (people, places, organizations, etc.)
            - Highlight relationships between entities mentioned in the question.
            Provide a structured classification and entity list.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Analyze all context documents in parallel
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for relevance to the question:
                - Identify mentions of key entities: {initial_analysis}
                - Extract relationships involving these entities
                - Summarize key facts related to the question""",
                context=doc
            ) for doc in self.problem_text.split('Document ')[1:]]
        )

        # Step 3: Reasoning Chain Construction - Connect entities across documents
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information from documents:
            {document_analyses}
            
            Construct a reasoning chain that connects the entities across documents:
            - Identify bridge entities that link documents
            - Follow the logical sequence of relationships
            - Ensure the chain leads to an answer to the question""",
            context=initial_analysis
        )

        # Step 4: Iterative Refinement - Improve the reasoning chain
        refined_chain = await self.revise(
            instruction="""Refine the reasoning chain:
            - Address any gaps or ambiguities
            - Add missing details or clarify relationships
            - Ensure the chain is logically sound and complete""",
            context=reasoning_chain
        )

        # Step 5: Answer Extraction and Validation - Extract precise answer
        answer_extraction = await self.generate(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the precise answer to the question:
            - Ensure the answer is factually correct
            - Validate against supporting facts from the documents
            - Format the answer as a short text span or yes/no response""",
            context=""
        )

        # Step 6: Final Validation - Ensure accuracy
        final_answer = await self.revise(
            instruction="""Validate the extracted answer:
            - Cross-check with supporting facts
            - Ensure it directly addresses the question
            - Correct any errors or inconsistencies""",
            context=answer_extraction
        )

        return final_answer