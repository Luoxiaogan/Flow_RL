# Workflow ID: limr_43_0
# Benchmark: limr
# Data Indices: [247, 106]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        
        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem to classify its type and identify key components:
            - Problem domain (e.g., algebra, geometry, combinatorics)
            - Variables, constants, and relationships
            - Constraints and objectives
            Provide structured output with clear headings.""",
            context=""
        )
        
        # Step 2: Strategy Selection
        if "algebra" in analysis.lower():
            strategy = "algebraic"
        elif "geometry" in analysis.lower():
            strategy = "geometric"
        elif "combinatorics" in analysis.lower():
            strategy = "combinatorial"
        else:
            strategy = "general"
        
        # Step 3: Parallel Exploration
        if strategy == "algebraic":
            paths = await asyncio.gather(
                self.generate(instruction="Solve using symbolic manipulation...", context=analysis),
                self.generate(instruction="Solve using numerical approximation...", context=analysis)
            )
        elif strategy == "geometric":
            paths = await asyncio.gather(
                self.generate(instruction="Solve using coordinate geometry...", context=analysis),
                self.generate(instruction="Solve using trigonometric identities...", context=analysis)
            )
        elif strategy == "combinatorial":
            paths = await asyncio.gather(
                self.generate(instruction="Solve using direct counting principles...", context=analysis),
                self.generate(instruction="Solve using generating functions...", context=analysis)
            )
        else:
            paths = await asyncio.gather(
                self.generate(instruction="Apply general mathematical reasoning...", context=analysis),
                self.generate(instruction="Explore alternative approaches...", context=analysis)
            )
        
        # Step 4: Ensemble Synthesis
        synthesis = await self.ensemble(
            instruction="Evaluate and synthesize the best solution from the explored paths.",
            contexts_list=paths
        )
        
        # Step 5: Validation and Refinement
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction="Validate the solution for correctness and completeness.",
                context=synthesis
            )
            if "error" in validation.lower():
                synthesis = await self.revise(
                    instruction=f"Address the following issues: {validation}",
                    context=synthesis
                )
            else:
                break
        
        # Step 6: Final Synthesis
        final_answer = await self.summarize(
            instruction="Condense the solution into a concise final answer (integer between 000 and 999).",
            context=synthesis
        )
        
        return final_answer