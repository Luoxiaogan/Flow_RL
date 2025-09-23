# Workflow ID: hotpotqa_31_0
# Benchmark: hotpotqa
# Data Indices: [389, 128]

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

        # Step 1: Initial Analysis - Classify question type and identify bridge entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and identify potential bridge entities:
            - What is the main entity in the question?
            - Which documents mention this entity?
            - Are there other entities that connect these documents?""",
            context=""
        )

        # Step 2: Parallel Exploration - Extract relevant information from documents
        documents = await self.generate(
            instruction="List all document titles and their key contents relevant to the question.",
            context=initial_analysis
        )
        document_tasks = [
            self.generate(
                instruction=f"Extract all facts related to bridge entities from {doc}.",
                context=initial_analysis
            ) for doc in documents.split("\n") if doc.strip()
        ]
        extracted_info = await asyncio.gather(*document_tasks)

        # Step 3: Reasoning Chain Construction - Connect extracted information
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information:
            {extracted_info}
            
            Build a reasoning chain that connects the facts to answer the question:
            - Start with the main entity in the question
            - Follow connections through bridge entities
            - End with the final answer.""",
            context="\n".join(extracted_info)
        )

        # Step 4: Answer Extraction - Extract precise answer
        answer = await self.generate(
            instruction=f"""From the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer in the required format (short text span or yes/no).""",
            context=reasoning_chain
        )

        # Step 5: Validation and Refinement - Validate answer and refine if necessary
        validation = await self.generate(
            instruction=f"""Validate the answer:
            {answer}
            
            Does it align with the supporting facts in the documents?""",
            context=reasoning_chain
        )
        if "error" in validation.lower() or "incomplete" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                {validation}""",
                context=answer
            )
            answer = refined_answer

        return answer