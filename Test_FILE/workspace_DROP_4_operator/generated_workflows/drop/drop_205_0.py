# Workflow ID: drop_205_0
# Benchmark: drop
# Data Indices: [153, 332]

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
        
        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 2: Question Analysis - Identify required operation(s)
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine the required operation(s). 
            Classify the question type (arithmetic, counting, comparison, span extraction) and identify key phrases indicating the operation(s).""",
            context=initial_analysis
        )
        
        # Step 3: Reference Resolution - Resolve pronouns and partial names
        reference_resolution = await self.generate(
            instruction=f"""Resolve pronouns and partial names in the question to their corresponding entities in the passage. 
            Use context clues from the passage and the extracted entities: {initial_analysis}.""",
            context=question_analysis
        )
        
        # Step 4: Operation Execution - Perform the identified operation(s)
        operation_execution = await asyncio.gather(
            self.generate(
                instruction=f"""Perform the identified operation(s) using the extracted entities and numbers. 
                Ensure the result matches the expected format (number, date, or exact text span). 
                Passage context: {initial_analysis}. Question context: {reference_resolution}.""",
                context=""
            ),
            self.ensemble(
                instruction="Synthesize multiple perspectives if needed.",
                contexts_list=[initial_analysis, question_analysis, reference_resolution]
            )
        )
        
        # Step 5: Validation and Refinement - Validate the result and refine if necessary
        final_result = await self.revise(
            instruction="""Validate the result against the passage and question. 
            Correct any errors or inconsistencies. Ensure the answer matches the expected format.""",
            context="\n".join(operation_execution)
        )
        
        return final_result