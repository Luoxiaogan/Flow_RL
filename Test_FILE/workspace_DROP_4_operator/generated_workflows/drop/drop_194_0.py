# Workflow ID: drop_194_0
# Benchmark: drop
# Data Indices: [247, 10]

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
        entity_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list:
            - Entities: [names, roles, descriptions]
            - Numbers: [values, units, what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        # Step 2: Classify the problem type
        problem_classification = await self.generate(
            instruction="""Classify the problem into one of these categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/less, first/last, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            - Multi-step (requires chaining multiple operations or facts)
            Provide reasoning for the classification.""",
            context=entity_extraction
        )

        # Step 3: Resolve references
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Passage: {self.problem_text}
            Extracted Entities: {entity_extraction}
            Problem Type: {problem_classification}""",
            context=entity_extraction
        )

        # Step 4: Identify and execute required operations
        if "arithmetic" in problem_classification.lower():
            # Perform arithmetic operations
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operations:
                Passage: {self.problem_text}
                Extracted Entities: {entity_extraction}
                Resolved References: {reference_resolution}
                Problem Type: {problem_classification}""",
                context=reference_resolution
            )
            intermediate_result = arithmetic_result
        elif "counting" in problem_classification.lower():
            # Perform counting operations
            counting_result = await self.generate(
                instruction=f"""Count the required entities or events:
                Passage: {self.problem_text}
                Extracted Entities: {entity_extraction}
                Resolved References: {reference_resolution}
                Problem Type: {problem_classification}""",
                context=reference_resolution
            )
            intermediate_result = counting_result
        elif "comparison" in problem_classification.lower():
            # Perform comparison operations
            comparison_result = await self.generate(
                instruction=f"""Compare the specified quantities or attributes:
                Passage: {self.problem_text}
                Extracted Entities: {entity_extraction}
                Resolved References: {reference_resolution}
                Problem Type: {problem_classification}""",
                context=reference_resolution
            )
            intermediate_result = comparison_result
        elif "span extraction" in problem_classification.lower():
            # Extract exact text span
            span_extraction_result = await self.generate(
                instruction=f"""Extract the exact text span from the passage:
                Passage: {self.problem_text}
                Extracted Entities: {entity_extraction}
                Resolved References: {reference_resolution}
                Problem Type: {problem_classification}""",
                context=reference_resolution
            )
            intermediate_result = span_extraction_result
        else:
            # Handle multi-step reasoning
            multi_step_result = await self.generate(
                instruction=f"""Chain multiple operations or facts to solve the problem:
                Passage: {self.problem_text}
                Extracted Entities: {entity_extraction}
                Resolved References: {reference_resolution}
                Problem Type: {problem_classification}""",
                context=reference_resolution
            )
            intermediate_result = multi_step_result

        # Step 5: Validate and refine intermediate results
        validation = await self.revise(
            instruction=f"""Validate the intermediate result:
            Intermediate Result: {intermediate_result}
            Passage: {self.problem_text}
            Extracted Entities: {entity_extraction}
            Resolved References: {reference_resolution}
            Problem Type: {problem_classification}""",
            context=intermediate_result
        )

        refined_result = await self.revise(
            instruction=f"""Refine the validated result to ensure correctness:
            Validated Result: {validation}
            Passage: {self.problem_text}
            Extracted Entities: {entity_extraction}
            Resolved References: {reference_resolution}
            Problem Type: {problem_classification}""",
            context=validation
        )

        # Step 6: Final answer synthesis
        final_answer = await self.summarize(
            instruction=f"""Condense the refined result into the final answer:
            Refined Result: {refined_result}
            Passage: {self.problem_text}
            Extracted Entities: {entity_extraction}
            Resolved References: {reference_resolution}
            Problem Type: {problem_classification}""",
            context=refined_result
        )

        return final_answer