# Workflow ID: mgsmbn_115_0
# Benchmark: mgsmbn
# Data Indices: [17]

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

        # PHASE 1: Decompose the problem into logical subproblems with dependencies
        decomposition_instruction = """
        Systematically break down this Bengali word problem into atomic subproblems.
        For each subproblem:
        - Identify the unknown being solved for
        - List the known values and relationships required
        - Specify dependencies (which other subproblems must be solved first)
        - Use simple, imperative language (e.g., "Calculate X using Y and Z")
        
        Focus on narrative structure: track entities (people, objects), events (births, transactions), 
        and temporal/causal relationships. Do not perform calculations yet.
        Format each subproblem as a dictionary with keys: id, description, dependencies.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: Generate multiple reasoning hypotheses in parallel
        hypothesis_instructions = [
            """
            Approach this as a chronological sequence of events.
            Reconstruct the timeline: what happened first, next, last.
            Express relationships as step-by-step narrative with embedded calculations.
            Explicitly state assumptions about implicit constraints (e.g., ages can't be negative).
            """,
            """
            Approach this as an algebraic system.
            Assign variables to unknowns, write equations based on relationships.
            Solve symbolically before substituting numbers.
            Show all equation transformations and substitutions.
            """,
            """
            Approach this through unit analysis and dimensional tracking.
            Identify all quantities with units (years, taka, items).
            Ensure unit consistency at every step.
            Convert units explicitly when needed.
            """
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # PHASE 3: Validate each hypothesis with executable code
        async def validate_hypothesis(hypothesis, idx):
            code_instruction = f"""
            Convert this reasoning into executable Python code:
            - Define all variables from problem text
            - Implement each calculation step explicitly
            - Include assertions for sanity checks (e.g., age > 0, quantity >= 0)
            - Print only the final numerical answer
            - Handle decimals and fractions precisely
            
            If the reasoning is incomplete or ambiguous, make minimal assumptions 
            and document them in comments.
            
            Reasoning to convert:
            {hypothesis}
            """
            try:
                result = await self.programmer(
                    instruction=code_instruction,
                    context=hypothesis,
                    max_retries=2
                )
                return {"hypothesis": hypothesis, "code_result": result, "valid": True, "index": idx}
            except Exception as e:
                return {"hypothesis": hypothesis, "error": str(e), "valid": False, "index": idx}

        validation_results = await asyncio.gather(
            *[validate_hypothesis(hyp, i) for i, hyp in enumerate(hypotheses)]
        )

        # PHASE 4: Revise invalid hypotheses
        revised_hypotheses = []
        for result in validation_results:
            if result["valid"]:
                revised_hypotheses.append(result["hypothesis"])
            else:
                revision_instruction = f"""
                This reasoning failed validation due to: {result.get('error', 'unknown error')}
                
                Revise the reasoning:
                - Fix logical inconsistencies
                - Ensure all quantities are non-negative and realistic
                - Make implicit assumptions explicit
                - Maintain chronological or algebraic coherence
                - Preserve the original approach (chronological/algebraic/unit-based)
                
                Original reasoning:
                {result['hypothesis']}
                """
                revised = await self.revise(
                    instruction=revision_instruction,
                    context=result['hypothesis']
                )
                # Re-validate revised hypothesis
                try:
                    revalidated = await self.programmer(
                        instruction=f"""
                        Convert this revised reasoning into executable Python code:
                        - Include assertions for all intermediate values
                        - Print only final numerical answer
                        
                        Revised reasoning:
                        {revised}
                        """,
                        context=revised,
                        max_retries=1
                    )
                    revised_hypotheses.append(revised)
                except Exception:
                    # If revision still fails, fall back to original for ensemble
                    revised_hypotheses.append(result['hypothesis'])

        # PHASE 5: Ensemble synthesis - select best validated solution
        ensemble_instruction = """
        You are given multiple solution approaches to the same Bengali math problem.
        Select the best answer based on:
        1. Mathematical consistency (all steps logically follow)
        2. Unit and constraint validity (no negative ages, fractional people, etc.)
        3. Completeness (all problem conditions addressed)
        4. Simplicity (prefer direct solutions over convoluted ones)
        
        Extract the final numerical answer from the selected solution.
        Output ONLY the number (integer or decimal) - no units, no explanation.
        """
        
        final_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=revised_hypotheses
        )

        # Clean and return final answer
        # Extract just the number from the ensemble result
        import re
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer.replace(',', ''))
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return first valid code result if ensemble failed
            for result in validation_results:
                if result["valid"]:
                    match = re.search(r'[-+]?\d*\.\d+|\d+', result["code_result"].replace(',', ''))
                    if match:
                        return float(match.group()) if '.' in match.group() else int(match.group())
            
            # Ultimate fallback: return 0 (should never happen in valid problems)
            return 0