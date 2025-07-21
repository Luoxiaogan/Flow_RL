# Workflow ID: gsm8k_71_1
# Benchmark: gsm8k
# Data Indices: [470, 924, 666]

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
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Novel workflow combining Iterative Refinement + Branching Logic (Conditional Reflection).
        Step 1: Generate an initial solution using Custom.
        Step 2: Review it to improve clarity and correctness.
        Step 3: Reflect on the reviewed solution — but only if the reflection indicates a critical flaw (e.g., "incomplete reasoning").
        Step 4: If reflection suggests issues, use FlexibleCustom in branching mode to explore alternative paths; otherwise, return the reviewed solution directly.
        """

        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break down all parts logically. Be explicit about assumptions."
        )

        # --- Step 2: First Review for Clarity & Structure ---
        reviewed_solution = await self.review(pre_solution=initial_solution)

        # --- Step 3: Reflect to Identify Potential Blind Spots ---
        reflection_text = await self.reflect(pre_solution=reviewed_solution)

        # --- Step 4: Conditional Branching Based on Reflection ---
        # If reflection suggests a major issue (e.g., contains keywords like "incomplete", "missing assumption", or "unclear step"), 
        # then perform a branching refinement using FlexibleCustom with structured steps.
        if any(keyword in reflection_text.lower() for keyword in ["incomplete", "missing assumption", "unclear step"]):
            refined_solution = await self.flexible_custom(
                custom_instruction="Based on the reflection below, re-solve the problem by exploring alternative interpretations or missing components.",
                reasoning_pattern="branching",
                steps=["re-evaluate_assumptions", "consider_alternatives", "reconstruct_solution"],
                use_structured_output=True
            )
        else:
            # No significant flaws found — return the reviewed solution as final
            refined_solution = reviewed_solution

        return refined_solution