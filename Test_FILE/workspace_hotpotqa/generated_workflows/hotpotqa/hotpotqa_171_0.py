# Workflow ID: hotpotqa_171_0
# Benchmark: hotpotqa
# Data Indices: [350, 43, 1059, 2360, 2363]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the answer with a custom operator, ensembles multiple solutions,
        and finally reviews the solution for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps and trace connections between pieces of information.
        reasoning_steps = [
            "identify_key_entities",
            "extract_facts_from_context",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_final_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities, and trace how they connect across different pieces of context.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Generate a synthesized answer based on the multi-hop reasoning.
        synthesis_prompt = "Based on the reasoning above, synthesize a clear and concise answer that directly addresses the question."
        synthesized_answer = await self.custom(instruction=synthesis_prompt)

        # Step 3: Ensembling - generate a few alternative answers using Custom for robustness
        # (even though we only use one, this simulates diversity in reasoning).
        solution_list = []
        for _ in range(3):  # Simulate generating 3 diverse solutions
            alt_answer = await self.custom(instruction="Generate an answer to the question by thinking through it step-by-step.")
            solution_list.append(alt_answer)

        # Ensemble the solutions to pick the most consistent and accurate one.
        final_answer = await self.sc_ensemble(solutions=solution_list)

        # Step 4: Review the final answer for correctness and clarity.
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer