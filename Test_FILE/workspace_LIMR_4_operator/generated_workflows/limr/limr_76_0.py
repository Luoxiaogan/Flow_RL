# Workflow ID: limr_76_0
# Benchmark: limr
# Data Indices: [189, 261]

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
        
        # Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="Analyze the problem and classify it into one of the following categories: geometry, number theory, algebra, combinatorics, probability, optimization, sequences. Identify key components, constraints, and what is being asked. Provide a structured summary.",
            context=""
        )
        
        # Parallel Exploration of Solution Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction="Using a direct counting approach, solve the problem. Show all steps and calculations.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Using generating functions, solve the problem. Show all steps and calculations.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Using recursive relations, solve the problem. Show all steps and calculations.",
                context=initial_analysis
            )
        )
        
        # Intermediate Verification and Refinement
        refined_approaches = await asyncio.gather(
            self.revise(
                instruction="Review the direct counting solution. Verify all calculations, check for logical consistency, and improve clarity where needed.",
                context=approaches[0]
            ),
            self.revise(
                instruction="Review the generating functions solution. Verify all calculations, check for logical consistency, and improve clarity where needed.",
                context=approaches[1]
            ),
            self.revise(
                instruction="Review the recursive relations solution. Verify all calculations, check for logical consistency, and improve clarity where needed.",
                context=approaches[2]
            )
        )
        
        # Ensemble Selection and Synthesis
        final_solution = await self.ensemble(
            instruction="Compare the refined solutions from direct counting, generating functions, and recursive relations. Select the most efficient and accurate solution. If multiple solutions are equally valid, synthesize them into a unified approach.",
            contexts_list=refined_approaches
        )
        
        # Final Verification and Presentation
        final_result = await self.revise(
            instruction="Conduct a final review of the selected solution. Ensure all steps are clear, calculations are accurate, and the answer is in the required format (integer between 000 and 999).",
            context=final_solution
        )
        
        return final_result