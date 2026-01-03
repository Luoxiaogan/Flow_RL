# Workflow ID: drop_103_0
# Benchmark: drop
# Data Indices: [472, 409]

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

        # Step 1: Initial Analysis (Extract Entities and Relationships)
        analysis_tasks = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]
                Format as structured list.""",
                context=""
            ),
            self.generate(
                instruction="""Identify pronoun references and map them to specific entities:
                - Resolve 'he', 'she', 'they', etc.
                - Map partial names to full names
                Provide mapping as key-value pairs.""",
                context=""
            )
        )
        entities_relations = analysis_tasks[0]
        pronoun_mapping = analysis_tasks[1]

        # Step 2: Problem Classification
        problem_type = await self.generate(
            instruction=f"""Classify the problem type based on the question:
            Entities and Relationships: {entities_relations}
            Pronoun Mapping: {pronoun_mapping}
            
            Possible types:
            - Arithmetic (addition, subtraction, comparison)
            - Counting (tally occurrences)
            - Comparison (compare attributes)
            - Span Extraction (exact text match)
            - Multi-Step (combine multiple operations)
            
            Provide classification and reasoning.""",
            context=entities_relations + "\n" + pronoun_mapping
        )

        # Step 3: Operation Execution (Conditional Branching)
        if "arithmetic" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                - Extract relevant numbers from: {entities_relations}
                - Identify operation (addition, subtraction, comparison)
                - Show calculation steps and final answer""",
                context=problem_type
            )
        elif "counting" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Count occurrences of specific entities/events:
                - Identify target entity/event from: {entities_relations}
                - Tally occurrences
                - Provide count as integer""",
                context=problem_type
            )
        elif "comparison" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Compare attributes:
                - Identify attributes to compare from: {entities_relations}
                - Perform comparison (greater, lesser, equal)
                - Provide result as text or number""",
                context=problem_type
            )
        elif "span extraction" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Extract exact text span:
                - Match question phrasing to passage
                - Ensure exact match
                - Provide span as-is""",
                context=problem_type
            )
        else:  # Multi-step or unknown type
            result = await self.generate(
                instruction=f"""Solve multi-step problem:
                - Break into sub-problems
                - Solve each sub-problem
                - Combine results into final answer""",
                context=problem_type
            )

        # Step 4: Validation and Formatting
        validated_result = await self.revise(
            instruction=f"""Validate and format the result:
            - Ensure numbers are plain integers/decimals
            - Ensure dates follow standard formats
            - Ensure text spans match passage exactly
            - Correct any formatting issues""",
            context=result
        )

        return validated_result