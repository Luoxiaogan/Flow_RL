# Workflow ID: drop_3_0
# Benchmark: drop
# Data Indices: [83, 380]

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

        # Step 1: Initial Analysis - Extract entities and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Classify the problem type:
            - Is it arithmetic, counting, comparison, span extraction, or multi-step?
            - What operations are required?""",
            context=""
        )

        # Step 2: Reference Resolution - Resolve pronouns and partial names
        resolved_references = await asyncio.gather(
            self.generate(
                instruction="Resolve all pronouns and partial names to their full forms.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Validate resolved references against the passage context.",
                context=initial_analysis
            )
        )
        resolved_context = "\n".join(resolved_references)

        # Step 3: Operation Execution - Conditional branching based on problem type
        analysis_summary = await self.summarize(
            instruction="Summarize the problem type and required operations.",
            context=resolved_context
        )

        if "arithmetic" in analysis_summary.lower():
            result = await self.generate(
                instruction="Perform the required arithmetic operations using extracted numbers.",
                context=resolved_context
            )
        elif "counting" in analysis_summary.lower():
            result = await self.generate(
                instruction="Count occurrences of the specified entities or events.",
                context=resolved_context
            )
        elif "comparison" in analysis_summary.lower():
            result = await self.generate(
                instruction="Compare the specified values or spans and determine the correct answer.",
                context=resolved_context
            )
        elif "span extraction" in analysis_summary.lower():
            result = await self.generate(
                instruction="Extract the exact text span that matches the question requirements.",
                context=resolved_context
            )
        else:  # Multi-step reasoning
            steps = await self.generate(
                instruction="Break down the multi-step reasoning into individual operations.",
                context=resolved_context
            )
            step_results = await asyncio.gather(
                *[self.generate(instruction=f"Execute step: {step}", context=resolved_context) for step in steps.split("\n")]
            )
            result = await self.ensemble(
                instruction="Combine results from all steps into a coherent answer.",
                contexts_list=step_results
            )

        # Step 4: Answer Synthesis - Ensemble to finalize the answer
        final_answer = await self.ensemble(
            instruction="Select the best answer or synthesize multiple perspectives if necessary.",
            contexts_list=[resolved_context, result]
        )

        # Step 5: Validation and Refinement - Iterative loop for error correction
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the answer against the expected format and requirements.",
                context=final_answer
            )
            if "error" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"Correct errors: {validation}",
                    context=final_answer
                )
            else:
                break

        return final_answer