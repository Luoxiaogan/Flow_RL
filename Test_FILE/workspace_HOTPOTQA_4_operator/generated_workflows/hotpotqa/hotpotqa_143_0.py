# Workflow ID: hotpotqa_143_0
# Benchmark: hotpotqa
# Data Indices: [120, 165]

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
            instruction="""Classify the question type (bridge, comparison, compositional).
            Extract key entities and terms that might connect different documents.
            Format the output as:
            Question Type: [type]
            Key Entities: [list of entities]""",
            context=""
        )

        # Step 2: Document Relevance Assessment
        doc_relevance = await self.generate(
            instruction=f"""Based on the extracted entities:
            {initial_analysis}
            
            Identify which documents contain relevant information.
            Focus on titles and initial sentences of each document.
            List the relevant documents and briefly explain why they are relevant.""",
            context=initial_analysis
        )

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.generate(
            instruction=f"""Identify entities or concepts that appear in multiple relevant documents:
            Relevant Documents:
            {doc_relevance}
            
            These entities will serve as bridge entities.
            List the bridge entities and explain their connections.""",
            context=doc_relevance
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain by following the connections between documents via the bridge entities:
            Bridge Entities:
            {bridge_entities}
            
            Ensure each step logically follows from the previous one.
            Present the reasoning chain as a sequence of connected facts.""",
            context=bridge_entities
        )

        # Step 5: Answer Extraction
        answer_extraction = await self.generate(
            instruction=f"""Locate the exact sentence or phrase in the final document that answers the question:
            Reasoning Chain:
            {reasoning_chain}
            
            Ensure the answer is factually correct and directly addresses the question.""",
            context=reasoning_chain
        )

        # Step 6: Validation and Refinement
        validation_refinement = await self.revise(
            instruction=f"""Validate the extracted answer against the original documents to ensure factual correctness:
            Extracted Answer:
            {answer_extraction}
            
            Refine the answer if any discrepancies are found.""",
            context=answer_extraction
        )

        # Step 7: Final Answer Compilation
        final_answer = await self.summarize(
            instruction=f"""Summarize the reasoning chain and the extracted answer into a concise response:
            Reasoning Chain:
            {reasoning_chain}
            Validated Answer:
            {validation_refinement}
            
            Include supporting facts from the documents.""",
            context=validation_refinement
        )

        return final_answer