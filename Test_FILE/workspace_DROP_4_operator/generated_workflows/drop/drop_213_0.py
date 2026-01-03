# Workflow ID: drop_213_0
# Benchmark: drop
# Data Indices: [368, 426]

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

        # Step 1: Initial Analysis to Classify Problem Type
        classification = await self.generate(
            instruction="""Classify the problem type:
            - Is it numerical, counting, comparison, or span extraction?
            - Does it require multi-step reasoning?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Extraction of Entities, Numbers, and Relationships
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        references_task = self.generate(
            instruction="""Identify and resolve all pronouns and partial names:
            - Map 'they', 'he', 'she', etc., to specific entities
            - Resolve partial names to full names where possible""",
            context=""
        )
        operations_task = self.generate(
            instruction=f"""Based on the problem classification ({classification}):
            - Identify the required operation(s) (e.g., addition, subtraction, counting)
            - Specify any constraints or conditions""",
            context=""
        )

        entities, references, operations = await asyncio.gather(entities_task, references_task, operations_task)

        # Step 3: Resolve References and Validate Operations
        resolved_references = await self.revise(
            instruction=f"""Resolve any remaining ambiguities in references:
            - Cross-check with extracted entities: {entities}
            - Ensure consistency across the passage""",
            context=references
        )
        validated_operations = await self.revise(
            instruction=f"""Validate the identified operations:
            - Ensure they align with the problem type: {classification}
            - Check for missing or incorrect operations""",
            context=operations
        )

        # Step 4: Execute Operations and Validate Results
        execution_task = self.generate(
            instruction=f"""Execute the validated operations:
            - Use extracted entities: {entities}
            - Apply resolved references: {resolved_references}
            - Follow the operations: {validated_operations}""",
            context=""
        )
        validation_task = self.generate(
            instruction=f"""Validate the execution results:
            - Ensure numerical precision
            - Match the expected answer format: {classification}""",
            context=""
        )

        execution_result, validation_result = await asyncio.gather(execution_task, validation_task)

        # Step 5: Ensemble to Synthesize Final Answer
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer:
            - Combine execution result: {execution_result}
            - Incorporate validation feedback: {validation_result}
            - Format according to the problem type: {classification}""",
            contexts_list=[execution_result, validation_result]
        )

        return final_answer