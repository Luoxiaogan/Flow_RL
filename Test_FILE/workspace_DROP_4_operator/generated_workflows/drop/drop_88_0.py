# Workflow ID: drop_88_0
# Benchmark: drop
# Data Indices: [187, 296]

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

        # Step 1: Generate Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Extract all named entities, numbers, and relationships.
            - Classify the problem type (numerical, logical, textual).
            - Identify key components and what is being asked.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Extraction and Classification
        entities_extraction, problem_classification = await asyncio.gather(
            self.generate(
                instruction="""Extract detailed entities:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ),
            self.generate(
                instruction="""Classify the problem:
                - Is it numerical, logical, or textual?
                - Does it require exact calculation or estimation?
                - Are there multiple valid approaches?
                - What's the expected answer format?""",
                context=initial_analysis
            )
        )

        # Step 3: Dynamic Instruction Construction
        if "numerical" in problem_classification.lower() and "exact" in problem_classification.lower():
            operation_instruction = """Solve with precise mathematical computation:
            - Show all algebraic steps
            - Maintain full precision
            - Double-check arithmetic
            - Present final answer with appropriate units"""
        elif "comparison" in problem_classification.lower():
            operation_instruction = """Identify and compare values:
            - Determine which is greater/lesser
            - Show reasoning for each comparison
            - Present final answer clearly"""
        else:
            operation_instruction = """Apply general problem-solving framework:
            - Use extracted entities and relationships
            - Follow logical reasoning steps
            - Present final answer in expected format"""

        # Step 4: Execute Operations
        solution_attempt = await self.generate(
            instruction=operation_instruction,
            context=f"{entities_extraction}

{problem_classification}"
        )

        # Step 5: Validation and Refinement
        validation = await self.generate(
            instruction="Validate the solution attempt for errors or inconsistencies.",
            context=solution_attempt
        )
        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"Fix issues: {validation}",
                context=solution_attempt
            )
        else:
            refined_solution = solution_attempt

        # Step 6: Ensemble Synthesis (if multiple paths)
        # Assuming we have multiple attempts stored in `attempts_list`
        attempts_list = [refined_solution]  # In practice, this would be populated differently
        final_answer = await self.ensemble(
            instruction="Synthesize the best answer from available attempts.",
            contexts_list=attempts_list
        )

        return final_answer