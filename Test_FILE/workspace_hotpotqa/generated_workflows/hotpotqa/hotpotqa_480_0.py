# Workflow ID: hotpotqa_480_0
# Benchmark: hotpotqa
# Data Indices: [3708, 2244, 2197, 1740, 3721]

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
        This is a workflow graph for multi-hop question answering with iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it using context.
        """
        # Step 1: Generate initial answer (first hop)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative refinement
        # Reasoning pattern: iterative, with steps for verification and synthesis
        refined_answer = await self.flexible_custom(
            custom_instruction="Iteratively refine the answer by checking facts against context and improving reasoning step-by-step.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "identify_gaps", "refine_answer"],
            max_iterations=3
        )
        
        return refined_answer