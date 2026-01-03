# Workflow ID: mgsmbn_126_0
# Benchmark: mgsmbn
# Data Indices: [191, 120]

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

        # Step 1: Decompose the problem into structured subproblems with dependencies
        decomposition_instruction = """
        Systematically break down this Bengali math word problem into atomic computational steps.
        For each step:
        - Identify the operation (addition, subtraction, multiplication, division, fraction, comparison)
        - Extract the numerical values and their semantic roles (who/what they belong to)
        - Specify dependencies: which previous steps must be completed before this one
        - Note units and constraints (e.g., "can't be negative", "must be integer")
        Format each subproblem as a clear, standalone calculation task.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Step 2: Parallel linguistic interpretation of ambiguous phrases
        key_phrases = await self.generate(
            instruction="""
            Extract all potentially ambiguous Bengali phrases that encode mathematical relationships.
            Examples: "ছোট" (younger/smaller), "বড়ো" (older/larger), "ভাগ" (fraction/part), "দ্বিগুণ" (double).
            For each phrase, provide 3 possible mathematical interpretations with confidence scores (1-5).
            Format: Phrase | Interpretation 1 (score) | Interpretation 2 (score) | Interpretation 3 (score)
            """,
            context=""
        )

        interpretations = await asyncio.gather(
            self.generate(instruction=f"Interpret key phrases mathematically:\n{key_phrases}\nFocus on age comparisons", context=""),
            self.generate(instruction=f"Interpret key phrases mathematically:\n{key_phrases}\nFocus on quantity changes", context=""),
            self.generate(instruction=f"Interpret key phrases mathematically:\n{key_phrases}\nFocus on temporal sequences", context="")
        )

        # Step 3: Ensemble consensus on phrase interpretations
        consensus = await self.ensemble(
            instruction="""
            Synthesize the three interpretations into one authoritative mapping.
            Resolve conflicts by:
            1. Prioritizing interpretations with explicit numerical support
            2. Choosing the interpretation that maintains unit consistency
            3. Selecting the option that produces plausible real-world results
            Output a clean dictionary: { "phrase": "mathematical_operation" }
            """,
            contexts_list=interpretations
        )

        # Step 4: Generate solution code based on decomposition and consensus
        code_instruction = f"""
        Generate Python code to solve the problem using the subproblem decomposition and phrase interpretations below.
        Subproblems: {subproblems}
        Consensus Interpretations: {consensus}
        
        Requirements:
        - Use only basic arithmetic operations
        - Track units implicitly (no unit conversion needed)
        - Assign final answer to variable 'answer'
        - No print statements or intermediate outputs
        - Handle fractions as decimals (e.g., 1/2 → 0.5)
        - Ensure all variables are initialized before use
        """
        code_result = await self.programmer(
            instruction=code_instruction,
            context=""
        )

        # Step 5: Validate and iteratively refine (max 2 iterations)
        answer = None
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""
                Validate the solution: {code_result}
                Check for:
                1. Negative results when context forbids them (ages, counts)
                2. Fractional results when integers are required (people, bees)
                3. Mathematical consistency with original relationships
                4. Plausibility (e.g., age sums, bee counts within reasonable bounds)
                If valid, output "VALID: [answer]". If invalid, explain why.
                """,
                context=code_result
            )

            if "VALID:" in validation:
                answer = validation.split("VALID:")[1].strip()
                break
            else:
                # Revise decomposition based on validation feedback
                revised_decomposition = await self.revise(
                    instruction=f"""
                    The solution failed validation: {validation}
                    Revise the problem decomposition:
                    - Re-express ambiguous relationships using consensus interpretations
                    - Add missing steps (e.g., implicit conversions, hidden operations)
                    - Ensure chronological/temporal order is preserved
                    Output revised subproblems with updated dependencies.
                    """,
                    context=str(subproblems)
                )
                subproblems = await self.decompose(
                    instruction=decomposition_instruction,
                    context=revised_decomposition
                )
                
                # Regenerate code with revised decomposition
                code_result = await self.programmer(
                    instruction=code_instruction.replace(str(subproblems), str(revised_decomposition)),
                    context=""
                )

        # Step 6: Final extraction and cleanup
        if answer is None:
            # Fallback: extract number from last code result
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', code_result)
            answer = numbers[-1] if numbers else "0"

        return answer