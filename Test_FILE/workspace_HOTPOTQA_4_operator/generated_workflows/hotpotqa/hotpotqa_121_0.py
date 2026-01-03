# Workflow ID: hotpotqa_121_0
# Benchmark: hotpotqa
# Data Indices: [499, 82]

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
        
        # Initial Analysis: Classify question type and extract insights
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Identify key entities, relationships, and required reasoning steps.
            Format the output as structured JSON with categories:
            - QuestionType: [bridge/comparison/compositional]
            - KeyEntities: [list of entities]
            - RequiredSteps: [steps to solve]""",
            context=""
        )
        
        # Extract entities and relationships in parallel
        documents = await self.generate(
            instruction="Extract all document titles and their content.",
            context=""
        )
        document_list = documents.split('\n\n')  # Assuming documents are separated by double newlines
        
        async def process_document(doc):
            return await self.generate(
                instruction=f"""Extract relevant entities and relationships from the following document:
                {doc}
                Focus on entities related to the question type: {initial_analysis}""",
                context=""
            )
        
        entity_results = await asyncio.gather(*[process_document(doc) for doc in document_list])
        
        # Ensemble to build reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize the extracted entities and relationships into a coherent reasoning chain.
            Connect documents through shared entities or comparative properties.
            Provide the chain as a sequence of logical steps.""",
            contexts_list=entity_results
        )
        
        # Extract precise answer
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain: {reasoning_chain}
            Extract the precise answer span from the final document.
            Ensure the answer is factually correct and matches the expected format.""",
            context=""
        )
        
        # Iterative refinement loop
        refined_answer = answer_extraction
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the answer: {refined_answer}",
                context=""
            )
            if "error" in validation.lower():
                refined_answer = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined_answer
                )
            else:
                break
        
        # Final summary
        final_output = await self.summarize(
            instruction="""Summarize the final answer and supporting facts.
            Ensure the output is concise and directly addresses the question.""",
            context=refined_answer
        )
        
        return final_output