# Workflow ID: hotpotqa_143_0
# Benchmark: hotpotqa
# Data Indices: [739, 2224, 3572, 3157]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem, 
                                                      reasoning_pattern="sequential",
                                                      steps=["identify_key_facts", "extract_entities", "trace_connections", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses flexible custom for structured multi-hop reasoning, then synthesizes with custom,
        ensembles multiple solutions, and finally reviews the best solution.
        """
        # Step 1: Use FlexibleCustom to break down the problem into smaller steps and trace connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace how each piece of information connects to the next."
        )

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Synthesize the multi-hop solution with a custom instruction for clarity
        synthesized_answer = await self.custom(
            instruction="Based on the multi-hop reasoning above, explain the solution clearly and concisely, ensuring all intermediate steps are logically connected."
        )

        # Step 4: Ensemble multiple candidate answers (including the direct and synthesized ones)
        ensemble_candidates = [multi_hop_solution, direct_answer, synthesized_answer]
        ensembled_answer = await self.sc_ensemble(solutions=ensemble_candidates)

        # Step 5: Review the ensembled answer to refine it further
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer