# Workflow ID: mbpp_66_0
# Benchmark: mbpp
# Data Indices: [4]

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

        # Step 1: Initial Analysis - Extract function name, inputs, and task description
        initial_analysis = await self.generate(
            instruction="""Extract key information from the problem:
            - Function name from assert statements
            - Input types and expected outputs from test cases
            - High-level task description from the natural language prompt
            Format the output as a structured summary.""",
            context=""
        )

        # Step 2: Parallel Fork - Generate multiple interpretations
        perspectives = await asyncio.gather(
            self.generate(instruction="Analyze the problem from a mathematical perspective...", context=initial_analysis),
            self.generate(instruction="Analyze the problem from a logical perspective...", context=initial_analysis),
            self.generate(instruction="Analyze the problem from a practical perspective...", context=initial_analysis)
        )

        # Step 3: Synthesize Interpretations
        synthesis = await self.ensemble(
            instruction="Combine these perspectives into a unified understanding of the problem...",
            contexts_list=perspectives
        )

        # Step 4: Conditional Branching - Classify problem type and generate code
        classification = await self.generate(
            instruction="""Classify the problem based on the synthesis:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - What is the expected answer format?""",
            context=synthesis
        )

        if "numerical" in classification.lower() and "exact" in classification.lower():
            code_attempt = await self.generate(
                instruction=f"""Generate Python code for the problem:
                - Use precise calculations
                - Include all necessary imports
                - Ensure proper indentation and formatting
                Synthesized understanding: {synthesis}""",
                context=""
            )
        elif "estimation" in classification.lower():
            code_attempt = await self.generate(
                instruction=f"""Generate Python code for the problem:
                - Use approximations where necessary
                - Include all necessary imports
                - Ensure proper indentation and formatting
                Synthesized understanding: {synthesis}""",
                context=""
            )
        else:
            code_attempt = await self.generate(
                instruction=f"""Generate Python code for the problem:
                - Follow best practices for readability and correctness
                - Include all necessary imports
                - Ensure proper indentation and formatting
                Synthesized understanding: {synthesis}""",
                context=""
            )

        # Step 5: Iterative Refinement Loop
        max_iterations = 3
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the generated code against the test cases:
                - Identify any errors or mismatches
                - Provide detailed feedback for improvement
                Generated code: {code_attempt}""",
                context=""
            )
            if "error" not in validation.lower():
                break
            code_attempt = await self.revise(
                instruction=f"""Revise the code based on validation feedback:
                - Address identified issues
                - Maintain proper formatting and structure
                Feedback: {validation}""",
                context=code_attempt
            )

        # Step 6: Final Synthesis and Output
        final_code = await self.revise(
            instruction="""Polish the final code:
            - Ensure proper imports
            - Maintain consistent indentation
            - Optimize for readability and performance""",
            context=code_attempt
        )

        return final_code