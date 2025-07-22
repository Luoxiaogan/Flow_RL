# Workflow ID: hotpotqa_414_0
# Benchmark: hotpotqa
# Data Indices: [448, 864, 2513, 2467, 1246]

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
        It first generates an initial answer, then refines it through iterative review and ensemble techniques.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential multi-hop reasoning to trace connections step-by-step
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Review the initial answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble multiple solutions (original, reviewed, and sequentially reasoned) for robustness
        solution_list = [initial_answer, reviewed_answer, sequential_reasoning]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer