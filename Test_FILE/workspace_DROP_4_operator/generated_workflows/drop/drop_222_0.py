# Workflow ID: drop_222_0
# Benchmark: drop
# Data Indices: [121, 212]

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
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve References and Clarify Ambiguities
        refined_analysis = await self.revise(
            instruction="Resolve any pronouns or partial names to their full forms and clarify ambiguous terms.",
            context=initial_analysis
        )

        # Step 3: Problem Classification
        problem_classification = await self.generate(
            instruction=f"""Classify the problem type based on the question:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, more, first/last, etc.)
            - Span Extraction (who did, what was the name, when did, etc.)
            - Multi-step (requires chaining multiple operations or facts)
            
            Given the refined analysis:
            {refined_analysis}""",
            context=""
        )

        # Step 4: Conditional Branching Based on Problem Type
        if "arithmetic" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Perform the required arithmetic operations:
                - Identify numbers and their relationships
                - Execute addition, subtraction, multiplication, or division as needed
                
                Given the refined analysis:
                {refined_analysis}""",
                context=""
            )
        elif "counting" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Count the occurrences of specific entities or events:
                - Identify the target entity or event
                - Tally the occurrences
                
                Given the refined analysis:
                {refined_analysis}""",
                context=""
            )
        elif "comparison" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Compare values or sequences:
                - Identify the items to compare
                - Determine the comparison criteria (greater, longer, first, last, etc.)
                
                Given the refined analysis:
                {refined_analysis}""",
                context=""
            )
        elif "span extraction" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                - Identify the question's focus
                - Pinpoint the exact phrase or sentence from the passage
                
                Given the refined analysis:
                {refined_analysis}""",
                context=""
            )
        else:  # Multi-step reasoning
            steps = await asyncio.gather(
                self.generate(
                    instruction=f"""First step: Identify and execute the initial operation.
                    Given the refined analysis:
                    {refined_analysis}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Second step: Chain the next operation based on the first result.
                    Given the refined analysis:
                    {refined_analysis}""",
                    context=""
                )
            )
            solution = await self.ensemble(
                instruction="Synthesize the results of the multi-step reasoning into a coherent answer.",
                contexts_list=steps
            )

        # Step 5: Answer Validation
        validated_solution = await self.ensemble(
            instruction="Validate the final answer by comparing it against multiple generated solutions.",
            contexts_list=[solution, refined_analysis]
        )

        return validated_solution