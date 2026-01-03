# Workflow ID: mgsmbn_64_0
# Benchmark: mgsmbn
# Data Indices: [30]

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

        # STEP 1: Decompose the problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Break down this Bengali math word problem into atomic, solvable subproblems. For each subproblem:
            - Clearly state what needs to be calculated or determined
            - Identify all required inputs and their sources
            - Specify dependencies on other subproblems
            - Flag any units, constraints, or real-world conditions
            - Highlight any implied operations (e.g., 'three times' implies multiplication)
            Return a list of subproblems with 'id', 'description', and 'dependencies'.""",
            context=""
        )

        # STEP 2: Parallel validation of subproblems via ensemble
        validation_tasks = []
        for sub in decomposition:
            task = self.generate(
                instruction=f"""Critically analyze this subproblem for accuracy and completeness:
                Subproblem: {sub['description']}
                - Is the mathematical operation correctly inferred?
                - Are all necessary values accounted for?
                - Are units and constraints properly noted?
                - Could there be alternative interpretations?
                Provide a revised version if needed, otherwise confirm 'VALID AS IS'.""",
                context=sub['description']
            )
            validation_tasks.append(task)
        
        validated_subproblems = await asyncio.gather(*validation_tasks)
        
        # Ensemble to resolve discrepancies
        final_subproblems = []
        for i, sub in enumerate(decomposition):
            consensus = await self.ensemble(
                instruction="""Choose the most accurate and complete version of this subproblem. 
                Prioritize interpretations that:
                - Explicitly state operations
                - Preserve unit information
                - Acknowledge real-world constraints
                - Minimize ambiguity""",
                contexts_list=[sub['description'], validated_subproblems[i]]
            )
            final_subproblems.append(consensus)

        # STEP 3: Classify problem type to determine solution strategy
        classification = await self.generate(
            instruction="""Classify this problem based on:
            1. Primary mathematical domain (arithmetic, proportion, sequence, rate, distribution, comparison)
            2. Computational complexity (simple calculation vs. multi-step algorithm)
            3. Need for unit conversion or tracking
            4. Presence of hidden steps or implicit operations
            5. Whether exact computation or logical reasoning dominates
            Output a JSON-like structure with keys: domain, complexity, units, hidden_steps, approach.""",
            context="\n".join(final_subproblems)
        )

        # STEP 4: Conditional routing based on classification
        if "computation" in classification.lower() or "algorithm" in classification.lower():
            # Route to programmer with explicit instructions
            solution = await self.programmer(
                instruction=f"""Generate Python code to solve this problem. Requirements:
                - Extract all numerical values and their meanings from context
                - Track units throughout (convert if necessary)
                - Implement step-by-step calculations matching the subproblems
                - Include assertions for real-world constraints (e.g., non-negative results)
                - Print ONLY the final numerical answer
                Context: {classification}
                Subproblems: {final_subproblems}""",
                context=classification
            )
        else:
            # Route to reasoning-based solution
            reasoning_attempt = await self.generate(
                instruction=f"""Solve this problem through logical reasoning. Requirements:
                - Follow the sequence of subproblems exactly
                - Show intermediate results explicitly
                - Justify each operation based on problem semantics
                - Verify plausibility at each step
                - State the final answer clearly
                Context: {classification}
                Subproblems: {final_subproblems}""",
                context=classification
            )
            
            # Iterative refinement (max 3 rounds)
            solution = reasoning_attempt
            for _ in range(3):
                critique = await self.generate(
                    instruction="""Critique this solution:
                    - Are all subproblems addressed?
                    - Are calculations correct and units consistent?
                    - Are there any missing intermediate steps?
                    - Does the final answer make real-world sense?
                    If no issues, respond 'VERIFIED'. Otherwise, list specific corrections needed.""",
                    context=solution
                )
                if "verified" in critique.lower():
                    break
                solution = await self.revise(
                    instruction=f"""Revise the solution based on this critique: {critique}
                    - Fix all identified errors
                    - Add missing steps
                    - Ensure unit consistency
                    - Maintain clear step-by-step reasoning""",
                    context=solution
                )

        # STEP 5: Extract and sanitize final numerical answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.
            - If multiple numbers exist, select the one that directly answers the original question
            - Remove all units, text, and explanations
            - Return as plain number (integer or decimal)
            - If uncertain, return the most prominently featured number""",
            context=solution
        )

        # Post-process to ensure clean numerical output
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer)
        
        # Handle edge case: if multiple numbers remain, take the last one (often the final answer)
        numbers = re.findall(r'\d+\.?\d*', cleaned_answer)
        if numbers:
            return numbers[-1]
        else:
            # Fallback: return raw extraction if regex fails
            return final_answer.strip()