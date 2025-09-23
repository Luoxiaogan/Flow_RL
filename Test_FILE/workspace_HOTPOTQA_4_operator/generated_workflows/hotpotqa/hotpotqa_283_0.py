# Workflow ID: hotpotqa_283_0
# Benchmark: hotpotqa
# Data Indices: [64]

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

        # Step 1: Analyze the question type and extract key entities
        question_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Is it a bridge, comparison, or compositional question?
            - Identify all key entities mentioned in the question.
            - Determine the expected answer format (yes/no, short phrase, etc.).""",
            context=""
        )

        # Step 2: Parallel document analysis
        document_analysis_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            document_analysis_tasks.append(
                self.generate(
                    instruction=f"""Analyze Document {i+1}:
                    - Extract all named entities (people, places, concepts).
                    - Identify key relationships and facts.
                    - Focus on information relevant to the question context.""",
                    context=question_analysis
                )
            )
        document_analyses = await asyncio.gather(*document_analysis_tasks)

        # Step 3: Identify bridge entities
        bridge_entities = await self.ensemble(
            instruction="""Identify entities that connect multiple documents:
            - Find common entities mentioned across documents.
            - Prioritize entities relevant to the question context.
            - Provide a ranked list of bridge entities.""",
            contexts_list=document_analyses
        )

        # Step 4: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entities: {bridge_entities}
            Construct a reasoning chain that connects the documents:
            - Start from the question and follow the connections.
            - Ensure the chain is logically consistent and factually accurate.
            - Highlight supporting facts from each document.""",
            context=question_analysis
        )

        # Step 5: Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Identify the exact text span that answers the question.
            - Verify that the answer is supported by facts from multiple documents.
            - Ensure the answer format matches the question requirements.""",
            context=reasoning_chain
        )

        # Optional refinement step
        refined_answer = await self.revise(
            instruction="Ensure clarity, precision, and factual correctness.",
            context=answer_extraction
        )

        return refined_answer