# Workflow ID: hotpotqa_250_0
# Benchmark: hotpotqa
# Data Indices: [75]

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
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities (people, organizations, locations).
            3. Highlight potential bridge entities connecting documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Document Exploration - Extract supporting facts for key entities
        entities = [line.split(":")[1].strip() for line in initial_analysis.split("\n") if "Entity" in line]
        fact_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all relevant facts about '{entity}' from the provided documents.
                Include explicit connections to other entities and documents.
                Format as bullet points.""",
                context=""
            )
            for entity in entities
        ]
        extracted_facts = await asyncio.gather(*fact_extraction_tasks)

        # Step 3: Reasoning Chain Construction - Build logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the following facts:
            {extracted_facts}
            
            Construct a logical reasoning chain connecting the question to the answer:
            - Start with the question.
            - Progress through intermediate facts.
            - End with the final answer.
            Ensure each step is supported by evidence from the documents.""",
            context=initial_analysis
        )

        # Step 4: Validation and Refinement - Check for consistency and completeness
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain:
            {reasoning_chain}
            
            Check for:
            - Logical consistency.
            - Completeness of connections.
            - Factual accuracy based on the documents.
            Highlight any issues or gaps.""",
            context=reasoning_chain
        )

        if "issue" in validation.lower() or "gap" in validation.lower():
            refined_chain = await self.revise(
                instruction=f"""Refine the reasoning chain to address:
                {validation}
                
                Ensure all steps are logically connected and factually accurate.""",
                context=reasoning_chain
            )
            reasoning_chain = refined_chain

        # Step 5: Final Answer Extraction - Extract precise answer span
        final_answer = await self.generate(
            instruction=f"""Extract the final answer from the reasoning chain:
            {reasoning_chain}
            
            Provide the exact answer span or yes/no response.
            Ensure the answer is supported by the reasoning chain.""",
            context=reasoning_chain
        )

        return final_answer