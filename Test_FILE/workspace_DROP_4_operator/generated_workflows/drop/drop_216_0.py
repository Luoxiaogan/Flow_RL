# Workflow ID: drop_216_0
# Benchmark: drop
# Data Indices: [241, 177]

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

        # Step 1: Extract all relevant entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Identify constraints and conditions
        constraints_identification = await self.generate(
            instruction=f"""Given these entities:
            {entities_extraction}
            
            Now identify all constraints and conditions:
            - Explicit constraints stated in problem
            - Implicit constraints from context
            - Physical or logical limitations
            - Boundary conditions""",
            context=entities_extraction
        )

        # Step 3: Define the solution space
        solution_space_definition = await self.generate(
            instruction=f"""With entities and constraints identified:
            Entities: {entities_extraction}
            Constraints: {constraints_identification}
            
            Define the solution space:
            - What are we solving for?
            - What methods are applicable?
            - What would constitute a valid answer?""",
            context=f"{entities_extraction}\n{constraints_identification}"
        )

        # Step 4: Analyze problem type and select strategy
        analysis = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?
            Provide structured classification.""",
            context=solution_space_definition
        )

        # Conditional branching based on problem type
        if "numerical" in analysis.lower() and "exact" in analysis.lower():
            result = await self.generate(
                instruction="""Solve with precise mathematical computation:
                - Show all algebraic steps
                - Maintain full precision
                - Double-check arithmetic
                - Present final answer with appropriate units""",
                context=solution_space_definition
            )
        elif "estimation" in analysis.lower():
            estimates = await asyncio.gather(
                self.generate(instruction="Estimate using order of magnitude...", context=solution_space_definition),
                self.generate(instruction="Estimate using dimensional analysis...", context=solution_space_definition),
                self.generate(instruction="Estimate using comparable examples...", context=solution_space_definition)
            )
            result = await self.ensemble(
                instruction="Synthesize estimates into best approximation",
                contexts_list=estimates
            )
        else:
            # Default comprehensive approach
            result = await self.generate(
                instruction="Apply general problem-solving framework...",
                context=solution_space_definition
            )

        # Step 5: Refine and validate the result
        refined_result = await self.revise(
            instruction="Improve clarity, add missing details, and verify calculations...",
            context=result
        )

        # Step 6: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Condense the final answer into the required format (number, date, or exact text span)...",
            context=refined_result
        )

        return final_answer