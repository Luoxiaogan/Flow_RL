# Workflow ID: mgsmbn_109_0
# Benchmark: mgsmbn
# Data Indices: [182]

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
        import json

        # LAYER 1: SEMANTIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this Bengali math word problem into minimal, ordered subproblems.
            For each subproblem:
            - Identify exactly what needs to be calculated or determined
            - Specify which entities/quantities are involved
            - List prerequisite subproblems by ID (comma-separated)
            - Flag any ambiguous references that need resolution
            Format each as a dictionary with keys: id, description, dependencies, ambiguities""",
            context=""
        )

        # LAYER 2: PARALLEL HYPOTHESIS GENERATION
        hypothesis_instructions = [
            """Generate a solution by LITERAL PARSING:
            - Extract all numbers and operations exactly as stated
            - Do not infer implicit quantities
            - Flag any step that requires assumption
            - Output as numbered steps with intermediate results""",
            
            """Generate a solution by CONTEXTUAL INFERENCE:
            - Infer implicit quantities (e.g., return journeys, shared items)
            - Resolve pronouns and ambiguous references using context
            - Justify each inference explicitly
            - Output as numbered steps with reasoning""",
            
            """Generate a solution by UNIT-AWARE MODELING:
            - Track units (টাকা, দিন, জিনিস) at every step
            - Convert units only when necessary and justified
            - Flag any unit mismatch or inconsistency
            - Output as steps with unit annotations"""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # LAYER 3: ADVERSARIAL VALIDATION
        validated_hypotheses = []
        for i, hypothesis in enumerate(hypotheses):
            validated = await self.revise(
                instruction=f"""CRITICALLY REVIEW this solution (Hypothesis {i+1}):
                - Assume it is WRONG. Find the flaw.
                - Check: math consistency, unit alignment, real-world plausibility
                - If no flaw found, explain why it's robust
                - Suggest ONE improvement even if correct
                - Preserve original structure but annotate errors/improvements""",
                context=hypothesis
            )
            validated_hypotheses.append(validated)

        # LAYER 4: ENSEMBLE SYNTHESIS WITH CONFLICT RESOLUTION
        final_reasoning = await self.ensemble(
            instruction="""SYNTHESIZE a unified solution from these three validated hypotheses:
            1. Identify points of AGREEMENT (highlight in [AGREE])
            2. Resolve CONFLICTS by:
               - Preferring unit-consistent interpretations
               - Choosing inferences with explicit justification
               - Rejecting solutions with unresolved ambiguities
            3. Output FINAL solution as:
               - Step-by-step reasoning (numbered)
               - Explicit intermediate values
               - Final answer boxed at end: \\boxed{{answer}}""",
            contexts_list=validated_hypotheses
        )

        # LAYER 5: SYMBOLIC-TO-NUMERIC EXECUTION
        for attempt in range(3):
            try:
                code_result = await self.programmer(
                    instruction=f"""Generate Python code that computes the final answer based ONLY on this reasoning:
                    {final_reasoning}
                    
                    Requirements:
                    - Define all variables explicitly
                    - Show intermediate calculations
                    - Output ONLY the final numerical answer (no text)
                    - Use float or int as appropriate""",
                    context=final_reasoning,
                    max_retries=1
                )
                
                # Extract numerical answer from code output
                lines = code_result.strip().split('\n')
                for line in reversed(lines):
                    if line.strip().replace('.', '').isdigit():
                        return float(line.strip()) if '.' in line else int(line.strip())
                
                # If no clean number found, try last line
                last_line = lines[-1].strip()
                if last_line.replace('.', '').isdigit():
                    return float(last_line) if '.' in last_line else int(last_line)
                    
            except Exception:
                continue

        # FALLBACK: Extract from final reasoning if code fails
        # Look for boxed answer pattern
        import re
        match = re.search(r'\\boxed\{([^}]+)\}', final_reasoning)
        if match:
            answer_str = match.group(1).strip()
            if '.' in answer_str:
                return float(answer_str)
            else:
                return int(answer_str)
        
        # Ultimate fallback: return 0 (should never happen)
        return 0