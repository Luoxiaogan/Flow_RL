# Workflow ID: hotpotqa_637_0
# Benchmark: hotpotqa
# Data Indices: [3183, 246, 1373, 404]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps and trace connections across multiple pieces of information.
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and connect facts across different parts of the context.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine and synthesize the solution with clear reasoning
        final_answer = await self.custom(
            instruction="Based on the reasoning above, provide a clear and concise answer with logical justification."
        )

        # Step 3: Use Review to critically assess the synthesized answer
        validated_answer = await self.review(pre_solution=final_answer)

        # Optional: Ensemble with a few alternative solutions (e.g., from multiple Custom runs) for robustness
        # Generate 2 additional answers using Custom with slightly varied instructions
        alt_solutions = []
        for i in range(2):
            alt = await self.custom(
                instruction=f"Provide an answer focusing on the key entities and their relationships. This is attempt {i+1}."
            )
            alt_solutions.append(alt)

        # Add original validated answer to ensemble list
        alt_solutions.append(validated_answer)

        # Final ensemble to select the best solution
        final_output = await self.sc_ensemble(solutions=alt_solutions)

        return final_output