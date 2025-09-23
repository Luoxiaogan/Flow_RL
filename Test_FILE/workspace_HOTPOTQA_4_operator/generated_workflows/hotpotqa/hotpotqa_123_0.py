# Workflow ID: hotpotqa_123_0
# Benchmark: hotpotqa
# Data Indices: [178]

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
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Highlight potential bridge entities that connect documents.
            Provide structured output with clear classification and extracted information.""",
            context=""
        )

        # Step 2: Conditional Branching Based on Question Type
        if "bridge" in analysis.lower():
            # Bridge Question: Find shared entities and trace relationships
            entities = await self.generate(
                instruction=f"""Extract bridge entities from the analysis:
                {analysis}
                
                Focus on entities that appear in multiple documents.
                List them with their associated documents and relationships.""",
                context=analysis
            )

            # Parallel Exploration: Process relevant documents
            document_tasks = []
            for entity in entities.split("\n"):
                task = self.generate(
                    instruction=f"""For the entity '{entity}':
                    - Trace its relationships across documents.
                    - Identify supporting facts that connect it to the question.
                    - Summarize key findings.""",
                    context=analysis
                )
                document_tasks.append(task)
            
            parallel_results = await asyncio.gather(*document_tasks)

            # Synthesis: Combine insights into a reasoning chain
            reasoning_chain = await self.ensemble(
                instruction="Merge insights into a coherent reasoning chain.",
                contexts_list=parallel_results
            )

        elif "comparison" in analysis.lower():
            # Comparison Question: Extract comparable attributes
            attributes = await self.generate(
                instruction=f"""Identify comparable attributes from the analysis:
                {analysis}
                
                Focus on properties or attributes mentioned in the question.
                List them with their associated values from different documents.""",
                context=analysis
            )

            # Parallel Exploration: Compare attributes across documents
            attribute_tasks = []
            for attribute in attributes.split("\n"):
                task = self.generate(
                    instruction=f"""Compare the attribute '{attribute}' across documents.
                    - Extract relevant values.
                    - Determine which document provides the correct information.
                    - Summarize findings.""",
                    context=analysis
                )
                attribute_tasks.append(task)
            
            parallel_results = await asyncio.gather(*attribute_tasks)

            # Synthesis: Build comparison result
            reasoning_chain = await self.ensemble(
                instruction="Combine comparisons into a final result.",
                contexts_list=parallel_results
            )

        else:
            # Compositional Question: Chain facts together
            reasoning_chain = await self.generate(
                instruction=f"""Chain facts together to answer the question:
                {analysis}
                
                Follow the logical sequence of facts across documents.
                Ensure each step connects to the next.""",
                context=analysis
            )

        # Step 3: Validation and Refinement
        validation = await self.revise(
            instruction=f"""Validate the reasoning chain:
            {reasoning_chain}
            
            Ensure all facts are factually correct and logically connected.
            Refine if necessary.""",
            context=reasoning_chain
        )

        # Step 4: Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final answer from the validated reasoning chain:
            {validation}
            
            Provide a short, factual answer directly.""",
            context=validation
        )

        return final_answer