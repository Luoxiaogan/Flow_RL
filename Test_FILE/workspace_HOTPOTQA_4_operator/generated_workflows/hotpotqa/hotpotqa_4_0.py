# Workflow ID: hotpotqa_4_0
# Benchmark: hotpotqa
# Data Indices: [12, 363]

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
        
        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities and relationships:
            - Identify the main subject of the question
            - Extract all named entities (people, places, organizations)
            - Identify relationships between entities
            - Provide structured output with clear labels""",
            context=""
        )
        
        # Step 2: Parallel Exploration - Generate reasoning paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""For bridge questions, identify potential bridge entities:
                - Find entities that connect the question subject to the desired property
                - Explore multiple possibilities if necessary
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""For comparison questions, gather relevant properties for each entity:
                - Identify properties mentioned in the question
                - Extract corresponding values from the documents
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""For compositional questions, combine multiple facts:
                - Identify facts that contribute to the answer
                - Explore different combinations of facts
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        )
        
        # Step 3: Path Validation and Refinement - Validate each reasoning path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this reasoning path:
                - Check logical consistency
                - Ensure factual support from documents
                - Add missing details if necessary
                Context: {path}""",
                context=path
            ) for path in reasoning_paths]
        )
        
        # Step 4: Synthesis and Decision - Select the best reasoning path
        best_path = await self.ensemble(
            instruction="""Select the most promising reasoning path:
            - Prioritize paths with strong factual support
            - Ensure coherence and alignment with the question
            - Choose the path that leads to the most precise answer""",
            contexts_list=refined_paths
        )
        
        # Step 5: Final Answer Extraction - Extract and validate the answer
        final_answer = await self.generate(
            instruction=f"""Extract the precise answer from the selected reasoning path:
            - Identify the exact answer span from the documents
            - Validate against supporting facts
            - Ensure the answer is short and factual
            Context: {best_path}""",
            context=best_path
        )
        
        return final_answer