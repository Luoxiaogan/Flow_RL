# Workflow ID: limr_172_0
# Benchmark: limr
# Data Indices: [213, 261]

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

        # STEP 1: Deep Problem Classification & Structural Analysis
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your output must include:

1. Problem Type Classification: Identify primary domain (algebra, number theory, combinatorics, geometry, etc.) and secondary domains if applicable.
2. Key Mathematical Objects: List all variables, functions, sets, or geometric entities involved.
3. Constraints & Conditions: Extract all explicit and implicit constraints, bounds, or conditions.
4. Target Output: Specify what is being asked for (expression, count, sum, proof, etc.) and its required format.
5. Potential Solution Pathways: Suggest 2-3 distinct mathematical approaches that could solve this problem, with brief rationale for each.
6. Known Theorems/Identities: List any relevant mathematical theorems, formulas, or identities that might apply.
7. Complexity Assessment: Estimate the number of steps required and potential pitfalls or non-obvious insights needed.

Format your response as a structured markdown document with clear section headers.""",
            context=""
        )

        # STEP 2: Conditional Branching Based on Problem Type
        # Extract problem type for branching (using simple keyword detection on classification output)
        problem_type = "general"
        if "algebra" in classification.lower() or "polynomial" in classification.lower() or "root" in classification.lower():
            problem_type = "algebraic"
        elif "number theory" in classification.lower() or "divisibility" in classification.lower() or "modular" in classification.lower():
            problem_type = "number_theoretic"
        elif "combinatorics" in classification.lower() or "counting" in classification.lower() or "permutation" in classification.lower():
            problem_type = "combinatorial"
        elif "geometry" in classification.lower():
            problem_type = "geometric"

        # STEP 3: Parallel Strategy Exploration (Diamond Pattern)
        strategy_instructions = {
            "algebraic": [
                "Apply symmetric polynomial theory and Vieta's formulas to express target expression in terms of elementary symmetric polynomials.",
                "Use substitution or variable transformation to simplify the given polynomial or expression before evaluation.",
                "Consider polynomial division or factorization to reveal hidden relationships between roots."
            ],
            "number_theoretic": [
                "Apply modular arithmetic and divisibility rules to reduce the problem to congruence equations.",
                "Use the Chinese Remainder Theorem or systematic case enumeration within given bounds.",
                "Transform the problem into a Diophantine equation and solve for integer solutions within constraints."
            ],
            "combinatorial": [
                "Apply combinatorial counting principles (inclusion-exclusion, generating functions, recursive relations).",
                "Model as a state space or graph and use dynamic programming or combinatorial enumeration.",
                "Use probabilistic method or expected value calculations if probability is involved."
            ],
            "geometric": [
                "Apply coordinate geometry by assigning coordinates to points and using distance/angle formulas.",
                "Use vector algebra or complex number representations for geometric transformations.",
                "Apply geometric theorems (Ceva, Menelaus, Power of a Point) or trigonometric identities."
            ],
            "general": [
                "Apply algebraic manipulation and equation solving techniques.",
                "Use logical deduction and case analysis based on given constraints.",
                "Apply brute-force enumeration within clearly defined bounds if other methods fail."
            ]
        }

        # Generate parallel solution attempts
        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on the problem classification and analysis, develop a complete solution using this strategy:
{strategy}

Include:
- Clear step-by-step reasoning
- All mathematical derivations
- Intermediate results and checks
- Final answer in boxed format

Use the following classification context:
{classification}""",
                context=classification
            ) for strategy in strategy_instructions[problem_type]]
        )

        # STEP 4: Decompose Problem Based on Type (Hierarchical Pattern)
        decomposition_instruction = f"""Decompose this {problem_type} problem into essential subproblems. For each subproblem:

- Clearly state what needs to be solved
- Identify dependencies on other subproblems
- Specify the mathematical tools or theorems required
- Estimate complexity (low/medium/high)

Prioritize subproblems that unlock subsequent steps. For algebraic problems, focus on symmetric expressions. For number theory, focus on modular conditions. For combinatorics, focus on counting principles.

Classification context:
{classification}"""

        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=classification
        )

        # Solve subproblems in dependency order
        solved_subproblems = {}
        for subproblem in subproblems:
            # Wait for dependencies
            if subproblem['dependencies']:
                dep_ids = [dep.strip() for dep in subproblem['dependencies'].split(',') if dep.strip()]
                # Wait for all dependencies to be solved (in real implementation, you'd track this properly)
                # For simplicity, we'll just proceed sequentially here
                pass
            
            # Generate solution for this subproblem
            sub_solution = await self.generate(
                instruction=f"""Solve this subproblem:
{subproblem['description']}

Use the following context:
Classification: {classification}
Previously solved subproblems: {solved_subproblems}

Show all work and verify your result.""",
                context=classification
            )
            solved_subproblems[subproblem['id']] = sub_solution

        # STEP 5: Code-Based Verification (Programmer Operator)
        # Extract potential computational components from classification
        code_context = await self.generate(
            instruction=f"""Based on the problem classification and analysis, identify any computational components that can be verified or solved via code:

- What variables need to be computed?
- What ranges or bounds are given?
- What conditions must be checked?
- What is the expected output format?

Extract specific parameters, bounds, and conditions that can be used in code.

Classification: {classification}
Solved subproblems: {solved_subproblems}""",
            context=classification
        )

        # Generate and execute code
        code_result = await self.programmer(
            instruction=f"""Write Python code to solve or verify the mathematical problem based on the following analysis:

{code_context}

Requirements:
- Handle all edge cases within given bounds
- Output must be an integer between 000 and 999
- Include verification steps where possible
- If multiple answers are possible, sum them as required
- Output only the final integer answer, padded to 3 digits

Example output format: "042" (not "42" or "The answer is 42")""",
            context=code_context,
            max_retries=3
        )

        # STEP 6: Ensemble Synthesis of All Approaches
        all_approaches = strategy_attempts + [str(solved_subproblems), code_result]
        
        final_answer = await self.ensemble(
            instruction="""Synthesize all solution approaches to determine the most reliable answer. Consider:

1. Consensus: Do multiple approaches yield the same result?
2. Rigor: Which approach has the most complete and error-free derivation?
3. Computational Verification: Does the code result match any analytical result?
4. Edge Case Handling: Which approach best handles boundary conditions?

If there is strong consensus (2+ matching results), select that answer. If results conflict, perform a deep cross-validation by checking key steps from each approach.

Output ONLY the final 3-digit integer answer (padded with leading zeros if necessary), with no additional text or explanation.""",
            contexts_list=all_approaches
        )

        # STEP 7: Final Formatting and Validation
        # Ensure output is exactly 3 digits
        formatted_answer = await self.revise(
            instruction="""Extract the final integer answer and format it as a 3-digit string with leading zeros if necessary.
For example: 42 becomes "042", 5 becomes "005", 123 remains "123".
If no clear integer answer is found, return "000".
Output ONLY the 3-digit string, nothing else.""",
            context=final_answer
        )

        # Clean up any potential extra text
        match = re.search(r'\b\d{1,3}\b', formatted_answer)
        if match:
            num = int(match.group())
            return f"{num:03d}"
        else:
            return "000"