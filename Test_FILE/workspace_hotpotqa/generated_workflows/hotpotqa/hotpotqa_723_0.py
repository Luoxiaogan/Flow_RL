# Workflow ID: hotpotqa_723_0
# Benchmark: hotpotqa
# Data Indices: [2014, 1024, 2345, 2770]

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
        It breaks down the problem into smaller steps, traces connections across context,
        and refines the answer through iterative review and ensemble methods.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace logical connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer for comparison
        solution_2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble the two solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[solution_2, refined_solution])

        return final_solution