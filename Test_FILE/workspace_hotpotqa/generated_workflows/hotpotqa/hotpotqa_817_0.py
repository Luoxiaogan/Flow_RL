# Workflow ID: hotpotqa_817_0
# Benchmark: hotpotqa
# Data Indices: [3314, 37, 2180, 3375, 3447]

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
        It uses multiple reasoning paths to enhance robustness and employs ensemble selection.
        """
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use Custom with step-by-step instruction to generate reasoned solution
        step_by_step_solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom with sequential reasoning pattern to trace multi-hop connections
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Use FlexibleCustom with iterative refinement for fact-checking and improvement
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with initial answer then verify against context",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )

        # Step 5: Ensemble all solutions to select the best one
        solutions = [direct_answer, step_by_step_solution, sequential_reasoning, iterative_refinement]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to ensure quality before return
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer