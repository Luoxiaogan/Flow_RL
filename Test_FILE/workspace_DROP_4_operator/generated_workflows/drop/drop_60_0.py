# Workflow ID: drop_60_0
# Benchmark: drop
# Data Indices: [419, 307]

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
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the question and identify required operations
        question_analysis = await self.generate(
            instruction=f"""Classify the question and identify required operations:
            Entities and Numbers: {entities_and_numbers}
            
            Analyze the question and determine:
            - Type of question (arithmetic, counting, comparison, span extraction, multi-step)
            - Required operations (addition, subtraction, counting, etc.)
            - Expected answer format (number, date, text span)""",
            context=entities_and_numbers
        )

        # Step 3: Parallel exploration based on question type
        if "counting" in question_analysis.lower():
            # Count all relevant instances
            count_operations = await asyncio.gather(
                self.generate(instruction="Count all instances of relevant actions...", context=entities_and_numbers),
                self.generate(instruction="Identify any overlapping or duplicate counts...", context=entities_and_numbers)
            )
            synthesis = await self.ensemble(
                instruction="Combine counts and resolve overlaps",
                contexts_list=count_operations
            )
        elif "comparison" in question_analysis.lower():
            # Identify entities and attributes for comparison
            comparison_operations = await asyncio.gather(
                self.generate(instruction="Extract attributes of entity A...", context=entities_and_numbers),
                self.generate(instruction="Extract attributes of entity B...", context=entities_and_numbers)
            )
            synthesis = await self.ensemble(
                instruction="Compare attributes and determine result",
                contexts_list=comparison_operations
            )
        else:
            # Default to multi-hop reasoning
            reasoning_operations = await asyncio.gather(
                self.generate(instruction="Analyze temporal relationships...", context=entities_and_numbers),
                self.generate(instruction="Analyze causal relationships...", context=entities_and_numbers)
            )
            synthesis = await self.ensemble(
                instruction="Synthesize reasoning paths into coherent answer",
                contexts_list=reasoning_operations
            )

        # Step 4: Validate and refine synthesis
        validated_synthesis = await self.revise(
            instruction="Validate and correct any errors in the synthesis...",
            context=synthesis
        )

        # Step 5: Extract final answer
        final_answer = await self.generate(
            instruction=f"""Extract the final answer:
            Validated Synthesis: {validated_synthesis}
            
            Ensure the answer matches the expected format (number, date, text span)
            and is exact to the passage.""",
            context=validated_synthesis
        )

        return final_answer