# Workflow ID: hotpotqa_136_0
# Benchmark: hotpotqa
# Data Indices: [2477, 2736, 951, 1631, 1540]

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
        It breaks down the problem into steps, traces connections across context, and refines the answer.
        """
        # Step 1: Use FlexibleCustom for sequential multi-hop reasoning to trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connecting them logically through the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        # Step 4: Review the ensembled solution to refine it further
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer