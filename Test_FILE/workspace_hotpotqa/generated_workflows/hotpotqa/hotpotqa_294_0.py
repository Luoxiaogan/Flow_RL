# Workflow ID: hotpotqa_294_0
# Benchmark: hotpotqa
# Data Indices: [3400, 3592, 812, 2050]

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
        It first breaks down the problem, then traces connections step-by-step, and finally refines the answer.
        """
        # Step 1: Break down the problem into smaller steps with flexible custom (sequential multi-hop)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured multi-hop solution
        answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve clarity and correctness
        refined_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble with multiple solutions (generate a few alternatives via custom prompts)
        alternative_solutions = [
            await self.custom(instruction="Solve this by breaking it down into clear, logical steps with detailed reasoning."),
            await self.custom(instruction="Explain how to solve this by identifying key facts and connecting them logically."),
            await self.custom(instruction="Provide a step-by-step reasoning path from the question to the final answer.")
        ]
        
        # Ensembling improves robustness by selecting the best among diverse approaches
        final_answer = await self.sc_ensemble(solutions=[refined_answer] + alternative_solutions)

        return final_answer