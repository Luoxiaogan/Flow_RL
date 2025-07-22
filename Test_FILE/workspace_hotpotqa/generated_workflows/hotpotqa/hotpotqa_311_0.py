# Workflow ID: hotpotqa_311_0
# Benchmark: hotpotqa
# Data Indices: [195, 1557, 724, 2158, 613]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_steps = [
            "identify_key_entities",
            "extract_facts_from_context",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_final_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on connecting information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the solution with clear reasoning
        synthesized_answer = await self.custom(
            instruction="Explain how to solve the problem with clear reasoning for each step, based on the extracted information."
        )

        # Step 3: Review the synthesized answer to ensure correctness
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Optionally, generate a direct answer as a fallback or ensemble candidate
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble the solutions to select the best one
        solution_list = [reviewed_answer, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer