# Workflow ID: hotpotqa_301_0
# Benchmark: hotpotqa
# Data Indices: [1193, 349, 3175, 263, 996]

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
        This is a streamlined workflow graph for multi-hop question answering.
        Uses FlexibleCustom with sequential reasoning to break down the problem,
        then optionally refines with Review and ensembles with ScEnsemble for robustness.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review for improved clarity or correctness
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Ensemble with AnswerGenerate for final confidence boost
        ensemble_solution = await self.sc_ensemble(solutions=[solution, refined_solution])

        return ensemble_solution