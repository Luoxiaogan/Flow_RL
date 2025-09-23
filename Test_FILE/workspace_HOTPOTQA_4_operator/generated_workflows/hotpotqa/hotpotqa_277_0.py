# Workflow ID: hotpotqa_277_0
# Benchmark: hotpotqa
# Data Indices: [399]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the main entities mentioned in the question.
            2. Determine the relationship or property being asked about.
            3. Classify the problem type (bridge, comparison, compositional).
            Provide structured output.""",
            context=""
        )

        # Step 2: Document Mapping
        entities = await self.generate(
            instruction=f"""From the analysis: {initial_analysis}
            Extract all named entities and generate a list of potential documents for each entity.
            Focus on documents that are likely to contain relevant information.""",
            context=initial_analysis
        )
        refined_documents = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine the list of documents for entity: {entity}. Remove irrelevant entries.",
                context=entities
            ) for entity in entities.split("\n")]
        )

        # Step 3: Bridge Entity Detection
        reasoning_chain = await self.ensemble(
            instruction=f"""Compare the content of the following documents: {refined_documents}
            Identify bridge entities or shared concepts that connect the documents.
            Construct a reasoning chain that links the entities through these bridge entities.""",
            contexts_list=refined_documents
        )

        # Step 4: Answer Extraction and Validation
        answer = await self.summarize(
            instruction=f"""From the reasoning chain: {reasoning_chain}
            Extract the precise answer to the question. Ensure the answer is factually correct and matches the expected format.""",
            context=reasoning_chain
        )

        # Step 5: Dynamic Adaptation
        validation = await self.generate(
            instruction=f"""Validate the answer: {answer}
            Cross-reference it with the supporting facts from the documents.
            If the answer is invalid or uncertain, suggest alternative reasoning paths.""",
            context=answer
        )
        if "error" in validation.lower() or "uncertain" in validation.lower():
            revised_answer = await self.revise(
                instruction=f"""Revise the answer based on validation feedback: {validation}
                Explore alternative reasoning paths or expand the document search.""",
                context=answer
            )
            return revised_answer

        return answer