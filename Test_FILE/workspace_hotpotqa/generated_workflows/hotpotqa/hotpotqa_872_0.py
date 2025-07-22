# Workflow ID: hotpotqa_872_0
# Benchmark: hotpotqa
# Data Indices: [880, 2762, 2605, 446]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It breaks down the problem into smaller steps, traces connections between pieces of information,
        and refines the solution through review and ensemble methods.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and how they connect across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Review the direct answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 4: Ensemble the results from flexible custom and reviewed answer
        solutions = [sequential_reasoning, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer