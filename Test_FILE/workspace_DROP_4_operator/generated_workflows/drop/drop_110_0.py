# Workflow ID: drop_110_0
# Benchmark: drop
# Data Indices: [82, 189]

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
        
        # Phase 1: Initial Analysis and Entity Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        entity_summary = await self.summarize(
            instruction="Condense the extracted entities into a structured summary highlighting key information.",
            context=entities
        )
        
        # Phase 2: Problem Classification and Strategy Selection
        classification = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?
            Provide structured classification.""",
            context=entity_summary
        )
        
        if "numerical" in classification.lower():
            # Phase 3: Detailed Reasoning and Operation Execution for Numerical Problems
            calculations = await asyncio.gather(
                self.generate(instruction="Perform required addition operations...", context=entity_summary),
                self.generate(instruction="Perform required subtraction operations...", context=entity_summary),
                self.generate(instruction="Perform required counting operations...", context=entity_summary)
            )
            result = await self.ensemble(
                instruction="Synthesize all numerical results into a coherent answer.",
                contexts_list=calculations
            )
        elif "logical" in classification.lower():
            # Phase 3: Detailed Reasoning and Operation Execution for Logical Problems
            comparisons = await asyncio.gather(
                self.generate(instruction="Compare entities based on given criteria...", context=entity_summary),
                self.generate(instruction="Sort entities based on given criteria...", context=entity_summary)
            )
            result = await self.ensemble(
                instruction="Synthesize all logical results into a coherent answer.",
                contexts_list=comparisons
            )
        else:
            # Phase 3: Detailed Reasoning and Operation Execution for Textual Problems
            spans = await asyncio.gather(
                self.generate(instruction="Extract exact text spans matching the question requirements...", context=entity_summary)
            )
            result = await self.ensemble(
                instruction="Select the most accurate text span as the answer.",
                contexts_list=spans
            )
        
        # Phase 4: Validation and Refinement
        validated_result = await self.revise(
            instruction="Validate the obtained results against the question and passage. Correct any discrepancies or refine the answer for clarity and accuracy.",
            context=result
        )
        
        for _ in range(3):  # Iterative refinement loop
            validation = await self.generate(
                instruction="Check if the current answer is satisfactory or needs further refinement.",
                context=validated_result
            )
            if "satisfactory" in validation.lower():
                break
            validated_result = await self.revise(
                instruction=f"Refine the answer based on feedback: {validation}",
                context=validated_result
            )
        
        return validated_result