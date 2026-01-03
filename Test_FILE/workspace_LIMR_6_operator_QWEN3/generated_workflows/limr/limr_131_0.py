# Workflow ID: limr_131_0
# Benchmark: limr
# Data Indices: [32, 237]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: META-ANALYSIS - Classify problem and propose strategies
        meta_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your task:

1. CLASSIFY the problem type by dominant mathematical domain (e.g., number theory, algebra, combinatorics, geometry).
2. IDENTIFY 2-3 distinct high-level solution strategies that could apply, explaining WHY each is relevant.
3. For each strategy, specify the key mathematical tools required (e.g., modular arithmetic, Vieta's formulas, generating functions).
4. FLAG any potential pitfalls or subtle constraints that could derail a naive approach.
5. OUTPUT in this exact format:
   DOMAIN: [domain]
   STRATEGY 1: [description] | TOOLS: [tools] | RISKS: [risks]
   STRATEGY 2: [description] | TOOLS: [tools] | RISKS: [risks]
   STRATEGY 3: [description] | TOOLS: [tools] | RISKS: [risks]

Be brutally honest about what makes this problem hard.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY EXPLORATION
        # Extract strategy descriptions for parallel processing
        strategy_lines = [line for line in meta_analysis.split('\n') if line.startswith('STRATEGY')]
        strategy_descriptions = []
        for line in strategy_lines:
            if '|' in line:
                desc = line.split('|')[0].replace('STRATEGY 1:', '').replace('STRATEGY 2:', '').replace('STRATEGY 3:', '').strip()
                strategy_descriptions.append(desc)

        # If no strategies extracted, default to comprehensive approach
        if len(strategy_descriptions) == 0:
            strategy_descriptions = [
                "Comprehensive algebraic and numerical approach",
                "Pattern recognition and case analysis",
                "Theoretical framework with proof-based reasoning"
            ]

        # Generate detailed solutions for each strategy in parallel
        strategy_tasks = []
        for i, strategy_desc in enumerate(strategy_descriptions[:3]):  # Limit to 3 strategies
            task = self.generate(
                instruction=f"""Develop a complete solution using this strategy: {strategy_desc}

Requirements:
- Show ALL mathematical steps with clear justifications
- Use appropriate notation and formalism
- Include intermediate calculations and checks
- Address the specific risks mentioned in the meta-analysis
- Conclude with a boxed final answer in the format \\boxed{{answer}}

If you encounter an obstacle, document it and propose a workaround.""",
                context=meta_analysis
            )
            strategy_tasks.append(task)

        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # STEP 3: ADVERSARIAL VALIDATION - Inject and correct errors
        adversarial_tasks = []
        for i, solution in enumerate(strategy_solutions):
            task = self.revise(
                instruction=f"""Adversarial Validation Protocol:

Assume this solution contains exactly ONE subtle error (logical, computational, or conceptual). Your tasks:

1. IDENTIFY the most likely error point (be specific: "Step 3 assumes commutativity without justification").
2. EXPLAIN why this is an error and how it affects the solution.
3. CORRECT the error and provide the revised solution.
4. VERIFY that the correction resolves the issue without introducing new errors.

Output format:
ERROR: [description]
CORRECTION: [revised solution section]
VERIFICATION: [confirmation of fix]""",
                context=solution
            )
            adversarial_tasks.append(task)

        validated_solutions = await asyncio.gather(*adversarial_tasks)

        # STEP 4: ENSEMBLE SYNTHESIS WITH WEIGHTED VOTING
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution from the candidates below. Evaluate each on:

1. MATHEMATICAL RIGOR (0-10): Are all steps justified? Are theorems applied correctly?
2. COMPUTATIONAL FEASIBILITY (0-10): Can this be executed without unreasonable complexity?
3. CONSTRAINT ALIGNMENT (0-10): Does it fully satisfy the problem's requirements?

Calculate a composite score (average of three axes). Select the solution with the highest score. If scores are within 1 point, MERGE the strongest elements.

OUTPUT ONLY the final answer in the format \\boxed{{answer}}. No explanations.""",
            contexts_list=validated_solutions
        )

        # STEP 5: PROGRAMMATIC VERIFICATION (if applicable)
        # Check if answer contains a boxed number for verification
        boxed_match = re.search(r'\\boxed\{(\d+)\}', final_answer)
        if boxed_match:
            proposed_answer = boxed_match.group(1)
            
            try:
                verification = await self.programmer(
                    instruction=f"""Verify the proposed answer {proposed_answer} for the original problem.

Write Python code that:
1. Implements the mathematical logic of the problem
2. Computes the correct answer independently
3. Compares it with {proposed_answer}
4. Outputs "VERIFIED" if they match, "DISCREPANCY" if not

Include all necessary calculations. Handle edge cases.""",
                    context=final_answer,
                    max_retries=2
                )
                
                # If discrepancy found, trigger refinement loop
                if "DISCREPANCY" in verification:
                    refined = await self.revise(
                        instruction=f"""The proposed answer {proposed_answer} failed programmatic verification. 
Re-examine your solution, identify the flaw, and provide the corrected answer in \\boxed{{}} format.
The verification result was: {verification}""",
                        context=final_answer
                    )
                    return refined
                    
            except Exception:
                # If programmer fails, return original answer
                pass

        return final_answer