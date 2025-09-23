# Workflow ID: drop_143_0
# Benchmark: drop
# Data Indices: [269, 29]

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
        
        # Step 1: Extract entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships from the passage:
            - Entities: People, teams, locations, etc.
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and connections between entities""",
            context=""
        )
        
        # Step 2: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to their corresponding entities:
            Passage Entities: {entities}
            Question References: Identify and map 'they', 'the team', etc., to specific entities.""",
            context=entities
        )
        
        # Step 3: Classify the problem type
        problem_type = await self.generate(
            instruction=f"""Classify the problem into one of the following categories:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, etc.
            - Span Extraction: Who did, what was, etc.
            - Multi-step: Requires combining multiple facts or operations.
            
            Passage: [Passage content]
            Question: [Question content]""",
            context=resolved_references
        )
        
        # Step 4: Parallel processing based on problem type
        if "arithmetic" in problem_type.lower():
            calculation = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Entities and Numbers: {resolved_references}
                Operation: Identify and execute addition, subtraction, etc.""",
                context=resolved_references
            )
            results = [calculation]
        elif "comparison" in problem_type.lower():
            comparison = await self.generate(
                instruction=f"""Compare the given values:
                Entities and Numbers: {resolved_references}
                Criteria: Greater than, less than, etc.""",
                context=resolved_references
            )
            results = [comparison]
        elif "span extraction" in problem_type.lower():
            span = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: [Passage content]
                Question: [Question content]""",
                context=resolved_references
            )
            results = [span]
        else:
            # Multi-step reasoning
            sub_problems = await self.generate(
                instruction=f"""Break the problem into sub-problems:
                Entities and Numbers: {resolved_references}
                Sub-problems: Identify and solve each part independently.""",
                context=resolved_references
            )
            sub_results = await asyncio.gather(
                *[self.generate(instruction=f"Solve sub-problem: {sp}", context=resolved_references) for sp in sub_problems.split("\n")]
            )
            results = sub_results
        
        # Step 5: Synthesize results
        final_result = await self.ensemble(
            instruction="Evaluate and select the most accurate and relevant result.",
            contexts_list=results
        )
        
        # Step 6: Validate and refine the final answer
        validated_answer = await self.revise(
            instruction=f"""Validate the final answer:
            Expected Format: Number, date, or exact text span.
            Final Result: {final_result}""",
            context=final_result
        )
        
        return validated_answer