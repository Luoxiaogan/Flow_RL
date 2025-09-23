# Workflow ID: hotpotqa_266_0
# Benchmark: hotpotqa
# Data Indices: [497]

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
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type:
            - Is it a bridge question (connecting entities across documents)?
            - Is it a comparison question (comparing properties)?
            - Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract relevant entities from documents
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities and their roles from Document {i+1}:
                - Focus on entities mentioned in the question ({question_analysis})
                - Include context for each entity""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        entities_per_document = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build reasoning chains across documents
        reasoning_chain = await self.ensemble(
            instruction=f"""Construct a reasoning chain using the extracted entities:
            - Identify shared entities across documents
            - Connect entities logically to address the question ({question_analysis})
            - Evaluate multiple potential chains and select the most plausible one""",
            contexts_list=entities_per_document
        )

        # Step 4: Extract the precise answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the exact answer span from the reasoning chain:
            - Ensure the answer directly addresses the question ({question_analysis})
            - Maintain factual accuracy and precision""",
            context=reasoning_chain
        )

        # Step 5: Validate and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Check for factual consistency with the documents
            - Ensure the answer format matches the question requirements
            - Revise if necessary""",
            context=answer_extraction
        )

        return refined_answer