# Workflow ID: hotpotqa_204_0
# Benchmark: hotpotqa
# Data Indices: [451, 219]

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

        # Step 1: Initial Analysis - Identify question type and key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and concepts.
            3. Identify potential bridge entities that connect documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Analyze all documents for relevance
        document_titles = re.findall(r"Document \d+: (.+?)\n", self.problem_text)
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document:
                1. Identify key entities and concepts.
                2. Highlight information related to the question.
                Document Title: {title}""",
                context=initial_analysis
            ) for title in document_titles]
        )

        # Step 3: Bridge Entity Identification - Confirm shared entities across documents
        bridge_entities = await self.ensemble(
            instruction="Identify and confirm bridge entities that connect documents.",
            contexts_list=document_analyses
        )

        # Step 4: Reasoning Chain Construction - Build logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities:
            {bridge_entities}
            
            Construct a reasoning chain that connects documents to answer the question.
            Specify the logical flow and supporting facts.""",
            context=initial_analysis
        )

        # Step 5: Answer Extraction - Locate precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the relevant document.
            Ensure the answer is factually correct and matches the expected format.""",
            context=""
        )

        # Step 6: Validation and Refinement - Validate and refine the answer
        validation = await self.generate(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Check for factual correctness and consistency with the reasoning chain.
            Identify any discrepancies or ambiguities.""",
            context=reasoning_chain
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