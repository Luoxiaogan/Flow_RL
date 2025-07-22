# Workflow ID: hotpotqa_8_0
# Benchmark: hotpotqa
# Data Indices: [3785, 2603, 853, 44, 3771]

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
                                                       steps=["identify_key_entities", "extract_facts", "trace_connections", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem, instruction="Break down the problem step by step and explain your reasoning for each step.")
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning via FlexibleCustom to extract and connect facts,
        then synthesizes with Custom, ensembles multiple solutions if needed,
        and finally reviews the result for accuracy.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(custom_instruction="Follow a logical sequence to identify key entities, extract relevant facts, trace connections between them, and synthesize an answer.")

        # Step 2: Generate a direct answer using AnswerGenerate for comparison
        direct_answer = await self.answer_generate()

        # Step 3: Synthesize the multi-hop solution into a clearer format
        synthesized_answer = await self.custom(instruction="Take the multi-hop solution and rephrase it clearly, ensuring each reasoning step is explicit and logically connected.")

        # Step 4: Ensemble the two answers to reduce errors
        ensemble_result = await self.sc_ensemble(solutions=[synthesized_answer, direct_answer])

        # Step 5: Review the final ensemble result for clarity and correctness
        final_answer = await self.review(pre_solution=ensemble_result)

        return final_answer