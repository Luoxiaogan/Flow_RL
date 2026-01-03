# Workflow ID: gsm8k_108_0
# Benchmark: gsm8k
# Data Indices: [230, 64]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, entities, and their relationships:
            - Numbers: [values and what they represent]
            - Entities: [people, objects, or concepts involved]
            - Relationships: [how entities interact with numbers]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Understand the question
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {extraction}
            
            Identify:
            - Problem type (e.g., sequential operations, rate, proportion)
            - Target variable (what is being asked for)
            Provide a clear classification.""",
            context=extraction
        )

        # Step 3: Build the calculation chain
        if "sequential" in classification.lower():
            # Sequential operations
            steps = await self.generate(
                instruction=f"""Construct a step-by-step calculation chain:
                {classification}
                
                Use the extracted information to build intermediate calculations.
                Show all steps explicitly.""",
                context=classification
            )
        elif "rate" in classification.lower():
            # Rate problems
            steps = await self.generate(
                instruction=f"""Solve the rate problem:
                {classification}
                
                Identify time, distance, and speed relationships.
                Build intermediate calculations step-by-step.""",
                context=classification
            )
        else:
            # Default approach for other problem types
            steps = await self.generate(
                instruction=f"""Solve the problem using a general approach:
                {classification}
                
                Build intermediate calculations step-by-step.""",
                context=classification
            )

        # Step 4: Validate intermediate results
        refined_steps = await self.revise(
            instruction="Verify and refine intermediate calculations. Correct any errors.",
            context=steps
        )

        # Step 5: Parallel exploration of alternative paths
        alternatives = await asyncio.gather(
            self.generate(instruction="Explore an alternative solution path.", context=refined_steps),
            self.generate(instruction="Explore another alternative solution path.", context=refined_steps)
        )

        # Step 6: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=[refined_steps] + alternatives
        )

        # Step 7: Return the final numerical answer
        answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return answer.strip()