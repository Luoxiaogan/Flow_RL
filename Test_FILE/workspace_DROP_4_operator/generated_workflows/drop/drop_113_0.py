# Workflow ID: drop_113_0
# Benchmark: drop
# Data Indices: [174, 344]

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
        
        # Initial Analysis: Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Identify problem type and required operations
        problem_classification = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?""",
            context=initial_analysis
        )
        
        # Conditional Branching based on problem type
        if "numerical" in problem_classification.lower():
            # Generate multiple solution attempts for numerical problems
            attempts = await asyncio.gather(
                self.generate(
                    instruction="Solve using precise mathematical computation...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Solve using estimation techniques...",
                    context=initial_analysis
                )
            )
            
            # Ensemble to select the best solution
            result = await self.ensemble(
                instruction="Select the most accurate and plausible solution",
                contexts_list=attempts
            )
        elif "counting" in problem_classification.lower():
            # Generate count and validate
            count_attempt = await self.generate(
                instruction="Count the relevant entities or events precisely...",
                context=initial_analysis
            )
            count_validation = await self.revise(
                instruction="Validate the count against the passage...",
                context=count_attempt
            )
            result = count_validation
        elif "comparison" in problem_classification.lower():
            # Generate comparison and validate
            comparison_attempt = await self.generate(
                instruction="Compare the specified entities or events...",
                context=initial_analysis
            )
            comparison_validation = await self.revise(
                instruction="Ensure the comparison is accurate and justified...",
                context=comparison_attempt
            )
            result = comparison_validation
        elif "span extraction" in problem_classification.lower():
            # Extract exact text span
            span_extraction = await self.generate(
                instruction="Extract the exact text span that answers the question...",
                context=initial_analysis
            )
            result = span_extraction
        else:
            # Default comprehensive approach for multi-step or complex problems
            multi_step_attempts = await asyncio.gather(
                self.generate(
                    instruction="Solve step-by-step, combining multiple facts...",
                    context=initial_analysis
                ),
                self.generate(
                    instruction="Use logical reasoning to connect different pieces of information...",
                    context=initial_analysis
                )
            )
            
            # Ensemble to synthesize the best multi-step solution
            result = await self.ensemble(
                instruction="Synthesize the most coherent and complete solution",
                contexts_list=multi_step_attempts
            )
        
        # Final Revision and Summarization
        refined_result = await self.revise(
            instruction="Refine the final result for clarity, accuracy, and completeness...",
            context=result
        )
        
        summary = await self.summarize(
            instruction="Condense the final result into a concise answer...",
            context=refined_result
        )
        
        return summary