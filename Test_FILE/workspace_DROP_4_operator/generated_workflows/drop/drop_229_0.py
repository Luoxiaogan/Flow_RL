# Workflow ID: drop_229_0
# Benchmark: drop
# Data Indices: [274, 105]

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
            instruction="""Extract all relevant information from the passage:
            - Entities: People, places, organizations
            - Numbers: All numerical values and their context
            - Relationships: Actions, events, connections between entities
            Format as structured list.""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify the problem based on the initial analysis:
            {initial_analysis}
            
            Determine:
            - Type: Numerical, Logical, Textual
            - Required Operations: Addition, Subtraction, Counting, Comparison, Span Extraction
            Provide structured classification.""",
            context=initial_analysis
        )

        # Step 3: Parallel Processing
        if "numerical" in classification.lower():
            numerical_result = await self.generate(
                instruction=f"""Perform numerical operations:
                {classification}
                
                Execute required arithmetic operations using extracted numbers.
                Show all steps and maintain precision.""",
                context=initial_analysis
            )
        else:
            numerical_result = ""

        if "logical" in classification.lower():
            logical_result = await self.generate(
                instruction=f"""Resolve logical references and combine information:
                {classification}
                
                Resolve pronouns and partial names to specific entities.
                Combine facts to answer the question.""",
                context=initial_analysis
            )
        else:
            logical_result = ""

        if "textual" in classification.lower():
            textual_result = await self.generate(
                instruction=f"""Extract exact text spans:
                {classification}
                
                Identify and extract exact spans matching the question.
                Ensure matches are verbatim from the passage.""",
                context=initial_analysis
            )
        else:
            textual_result = ""

        # Gather parallel results
        parallel_results = await asyncio.gather(
            self.revise(instruction="Refine numerical result", context=numerical_result),
            self.revise(instruction="Refine logical result", context=logical_result),
            self.revise(instruction="Refine textual result", context=textual_result)
        )

        # Step 4: Synthesis and Validation
        synthesis = await self.ensemble(
            instruction="Synthesize refined results into final answer",
            contexts_list=parallel_results
        )

        final_answer = await self.revise(
            instruction="Validate and format final answer to match expected format",
            context=synthesis
        )

        return final_answer