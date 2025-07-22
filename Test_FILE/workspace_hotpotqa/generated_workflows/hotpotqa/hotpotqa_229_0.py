# Workflow ID: hotpotqa_229_0
# Benchmark: hotpotqa
# Data Indices: [3840, 469, 2217, 2076]

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
        This is a workflow graph for multi-hop question answering.
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate initial answer directly (baseline)
        direct_answer = await self.answer_generate()

        # Step 2: Generate reasoning-based answers with different instructions
        step_by_step = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        chain_of_thought = await self.custom(instruction="Solve this by thinking through each logical connection step-by-step, showing how one piece of information leads to the next.")
        
        # Step 3: Use flexible custom for structured multi-hop reasoning
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the three solutions to find the most robust answer
        solutions = [direct_answer, step_by_step, chain_of_thought, multi_hop_reasoning]
        ensemble_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine and validate the ensemble answer
        final_answer = await self.review(pre_solution=ensemble_answer)

        return final_answer