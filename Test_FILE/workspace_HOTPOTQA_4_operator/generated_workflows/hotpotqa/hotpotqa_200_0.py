# Workflow ID: hotpotqa_200_0
# Benchmark: hotpotqa
# Data Indices: [439, 239]

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

        # Step 1: Initial Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the question type (bridge, comparison, compositional).
            - Identify key entities and expected answer format.
            - Highlight relevant documents and sections.""",
            context=""
        )

        # Step 2: Parallel Document Parsing
        # Extract entities and facts from each document
        documents = re.findall(r"Document \d+:.*?\n(.*?)\n\n", self.problem_text, re.DOTALL)
        parsed_documents = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract relevant information from this document:
                - Identify entities mentioned in the question.
                - Highlight supporting facts and sentences.
                Document content: {doc}""",
                context=problem_analysis
            ) for doc in documents]
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from parsed documents:
            - Identify shared entities or comparison targets.
            - Construct a logical reasoning chain connecting documents.
            - Ensure all steps are factually supported.""",
            contexts_list=parsed_documents
        )

        # Step 4: Answer Extraction and Validation
        extracted_answer = await self.generate(
            instruction=f"""Extract the precise answer based on the reasoning chain:
            - Ensure the answer is factually correct and supported by evidence.
            - Format as a short text span or yes/no response.
            Reasoning chain: {reasoning_chain}""",
            context=problem_analysis
        )

        # Step 5: Iterative Refinement
        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            - Improve clarity and precision.
            - Validate against the reasoning chain.
            - Correct any errors or ambiguities.""",
            context=extracted_answer
        )

        return refined_answer