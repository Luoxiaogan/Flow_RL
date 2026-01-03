# Workflow ID: gsm8k_138_0
# Benchmark: gsm8k
# Data Indices: [42, 90]

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

        # Initial analysis to classify the problem type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and identify key components:
            - Classify the problem type (sequential, rate, distribution, proportions, multi-entity)
            - Extract all numerical values and their context
            - Identify what the question asks for""",
            context=""
        )

        # Parallel extraction of numbers, entities, and relationships
        numbers_extraction, entities_extraction, relationships_extraction = await asyncio.gather(
            self.generate(
                instruction="Extract all numerical values and their units/contexts",
                context=initial_analysis
            ),
            self.generate(
                instruction="Identify all named entities and their roles",
                context=initial_analysis
            ),
            self.generate(
                instruction="Identify relationships between entities and numbers",
                context=initial_analysis
            )
        )

        # Sequential processing of operations
        operations_sequence = await self.generate(
            instruction=f"""Based on the extracted information:
            Numbers: {numbers_extraction}
            Entities: {entities_extraction}
            Relationships: {relationships_extraction}
            
            Define the sequence of arithmetic operations needed to solve the problem""",
            context=initial_analysis
        )

        # Perform step-by-step calculations
        steps = operations_sequence.split('\n')
        intermediate_results = []
        for step in steps:
            result = await self.generate(
                instruction=f"Perform the calculation: {step}",
                context="\n".join(intermediate_results)
            )
            intermediate_results.append(result)

        # Validation and refinement of intermediate results
        validated_results = []
        for result in intermediate_results:
            validation = await self.revise(
                instruction="Validate the calculation and refine if necessary",
                context=result
            )
            validated_results.append(validation)

        # Final synthesis into a single numerical answer
        final_answer = await self.ensemble(
            instruction="Combine all validated results into a final numerical answer",
            contexts_list=validated_results
        )

        return final_answer