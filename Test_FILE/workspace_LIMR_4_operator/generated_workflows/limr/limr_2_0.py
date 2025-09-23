# Workflow ID: limr_2_0
# Benchmark: limr
# Data Indices: [148, 204]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Geometry
            - Number Theory
            - Combinatorics
            - Algebra
            - Optimization
            - Sequence and Series
            
            Identify key components:
            - Variables and constants
            - Constraints and relationships
            - Expected answer format
            Provide structured output.""",
            context=""
        )

        # Step 2: Solution Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(instruction="Solve using algebraic manipulation...", context=analysis),
            self.generate(instruction="Solve using combinatorial arguments...", context=analysis),
            self.generate(instruction="Solve using geometric transformations...", context=analysis),
            self.generate(instruction="Solve using optimization techniques...", context=analysis)
        )

        # Step 3: Intermediate Validation
        validated_strategies = []
        for strategy in strategies:
            validation = await self.generate(
                instruction=f"Validate the following solution: {strategy}. Check for logical consistency, mathematical correctness, and alignment with constraints.",
                context=analysis
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues identified: {validation}",
                    context=strategy
                )
                validated_strategies.append(refined)
            else:
                validated_strategies.append(strategy)

        # Step 4: Synthesis and Selection
        synthesis = await self.ensemble(
            instruction="Compare all validated strategies. Select the most complete, correct, and elegant solution.",
            contexts_list=validated_strategies
        )

        # Step 5: Final Refinement
        final_solution = await self.revise(
            instruction="Refine the selected solution. Ensure clarity, precision, and adherence to problem requirements. Verify all calculations and reasoning steps.",
            context=synthesis
        )

        # Step 6: Output Generation
        final_answer = await self.summarize(
            instruction="Summarize the final solution. Present a concise, well-structured answer.",
            context=final_solution
        )

        return final_answer