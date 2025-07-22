# Workflow ID: hotpotqa_553_0
# Benchmark: hotpotqa
# Data Indices: [2388, 1413, 1852, 1062]

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
        self.custom = operator.Custom(self.config, self.problem, instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")
        self.review = operator.Review(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning via FlexibleCustom to extract and connect facts,
        then synthesizes with Custom, reviews for accuracy, and ensembles multiple answers if needed.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning (sequential)
        multi_hop_solution = await self.flexible_custom(custom_instruction="Focus on connecting information across different parts of the context.")

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Synthesize solution from multi-hop extraction
        synthesis = await self.custom(instruction="Based on the extracted facts, synthesize a clear and accurate answer with step-by-step reasoning.")

        # Step 4: Review the synthesized solution for errors or gaps
        reviewed_solution = await self.review(pre_solution=synthesis)

        # Step 5: Ensemble with direct answer to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return ensemble_solution