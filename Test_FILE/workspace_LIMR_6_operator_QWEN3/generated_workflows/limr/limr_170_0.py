# Workflow ID: limr_170_0
# Benchmark: limr
# Data Indices: [40, 291]

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

        # STEP 1: META-CLASSIFICATION - Understand the problem's nature, structure, and strategy requirements
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem. Address:

1. Problem Type Classification:
   - Is this primarily algebraic, combinatorial, number-theoretic, geometric, or optimization?
   - Does it involve sequences, series, polynomials, modular arithmetic, or complex numbers?
   - Is it proof-based, computational, or existential?

2. Complexity Assessment:
   - How many distinct reasoning steps are likely required?
   - Are there interdependent subproblems or can it be solved in one insight?
   - Does it require advanced techniques (generating functions, induction, coordinate transforms)?

3. Solution Strategy Recommendations:
   - List 2-3 promising mathematical approaches (e.g., "Use roots of unity filter for alternating binomial sums")
   - Identify potential computational bottlenecks or symbolic manipulation needs
   - Note any constraints (integer answers, modular conditions, positivity requirements)

4. Decomposability Analysis:
   - Can this be broken into independent subproblems? If so, describe them.
   - Are there clear prerequisites or dependencies between steps?

Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: DYNAMIC ROUTING - Choose between decomposition or parallel exploration based on classification
        routing_decision = await self.generate(
            instruction=f"""Based on this classification:
{classification}

Decide the optimal solution architecture:

Option A (Hierarchical Decomposition): If the problem has clear, interdependent subproblems with prerequisites, choose this.
Option B (Parallel Exploration): If multiple independent solution paths are viable, choose this.
Option C (Direct Computation): If the problem is straightforward and computational, choose this.

Justify your choice in 2-3 sentences. Then output ONLY the letter (A, B, or C) on the last line.""",
            context=classification
        )
        
        strategy_choice = routing_decision.strip().split('\n')[-1].strip()

        # STEP 3A: HIERARCHICAL DECOMPOSITION PATH
        if strategy_choice == "A":
            decomposition = await self.decompose(
                instruction=f"""Based on this analysis:
{classification}

Decompose the problem into minimal, solvable subproblems. For each subproblem:
- Clearly state what needs to be computed or proven
- Specify any mathematical tools or theorems required
- List prerequisite subproblems by ID
- Ensure the final subproblem yields the required answer (integer 000-999)

Prioritize logical dependencies and mathematical prerequisites.""",
                context=classification
            )
            
            # Execute subproblems in dependency order
            solved_subproblems = {}
            for subproblem in decomposition:
                # Wait for dependencies
                deps = subproblem.get('dependencies', "").split(',') if subproblem.get('dependencies') else []
                for dep_id in deps:
                    dep_id = dep_id.strip()
                    if dep_id and dep_id not in solved_subproblems:
                        # This shouldn't happen in a valid topological sort, but handle gracefully
                        continue
                
                # Generate solution for this subproblem
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem:
{subproblem['description']}

Use results from these solved subproblems if needed:
{json.dumps({k: v for k,v in solved_subproblems.items() if k in deps}, indent=2)}

Show all mathematical steps. Verify intermediate results. Output should be self-contained and rigorous.""",
                    context=json.dumps(solved_subproblems)
                )
                
                # Verify the solution
                verified_solution = await self.revise(
                    instruction="""Critically verify this mathematical solution:
- Check all algebraic manipulations for errors
- Confirm boundary conditions and constraints are respected
- Ensure final output format is correct (integer 000-999 if applicable)
- If errors found, correct them and explain the fix

Output the verified solution only.""",
                    context=sub_solution
                )
                
                solved_subproblems[subproblem['id']] = verified_solution
            
            # Final answer should be in the last subproblem (assuming topological order)
            final_answer_context = list(solved_subproblems.values())[-1] if solved_subproblems else ""

        # STEP 3B: PARALLEL EXPLORATION PATH
        elif strategy_choice == "B":
            # Generate 3 different solution approaches in parallel
            approach_instructions = [
                """Solve using algebraic and symbolic manipulation techniques. Focus on:
- Polynomial identities, series expansions, or functional equations
- Algebraic transformations and substitutions
- Exact symbolic computation
Show all steps and verify each transformation.""",
                
                """Solve using combinatorial or number-theoretic reasoning. Focus on:
- Counting principles, bijections, or combinatorial identities
- Modular arithmetic, divisibility, or prime factorization
- Recursive relationships or generating functions
Justify each combinatorial step rigorously.""",
                
                """Solve using computational or algorithmic approach. Focus on:
- Writing precise mathematical code to compute the answer
- Handling edge cases and boundary conditions
- Ensuring numerical precision and integer constraints
Include the code and its output as part of your solution."""
            ]
            
            approach_tasks = [
                self.generate(instruction=instr, context=classification)
                for instr in approach_instructions
            ]
            raw_approaches = await asyncio.gather(*approaches_tasks)
            
            # Verify each approach
            verification_tasks = [
                self.revise(
                    instruction="""Verify this mathematical solution:
- Check all steps for logical consistency and computational accuracy
- Ensure the answer is an integer between 000 and 999 as required
- Identify any hidden assumptions or edge cases not considered
- If errors found, correct them and explain

Output only the verified solution.""",
                    context=approach
                )
                for approach in raw_approaches
            ]
            verified_approaches = await asyncio.gather(*verification_tasks)
            
            # Synthesize the best answer
            final_answer_context = await self.ensemble(
                instruction="""Select the most mathematically sound solution from these candidates:
- Evaluate based on logical rigor, completeness, and adherence to constraints
- Prefer solutions that explicitly verify their answer format (integer 000-999)
- If multiple are correct, select the most elegant or efficient
- If none are fully correct, synthesize a new solution combining the best elements

Output only the final answer as an integer between 000 and 999.""",
                contexts_list=verified_approaches
            )

        # STEP 3C: DIRECT COMPUTATION PATH
        else:  # strategy_choice == "C"
            direct_solution = await self.generate(
                instruction=f"""Based on this classification:
{classification}

Solve the problem directly with minimal steps. Focus on:
- Immediate computational or algebraic insight
- Leveraging known identities or theorems for quick resolution
- Verifying the answer is an integer between 000 and 999

Show your work concisely but completely.""",
                context=classification
            )
            
            verified_solution = await self.revise(
                instruction="""Verify this solution:
- Double-check all calculations and logic
- Confirm answer format is correct (integer 000-999)
- Ensure no edge cases were overlooked

Output only the verified final answer.""",
                context=direct_solution
            )
            
            final_answer_context = verified_solution

        # STEP 4: FINAL EXTRACTION AND FORMATTING
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer from the following solution.
The answer must be an integer between 000 and 999.
If multiple numbers appear, select the one that answers the original question.
If no clear answer, re-express the solution to isolate the final integer.

Output ONLY the three-digit integer (e.g., "042", "123", "999").""",
            context=final_answer_context
        )
        
        # Clean and return the answer
        answer = final_answer.strip()
        if len(answer) == 1:
            answer = "00" + answer
        elif len(answer) == 2:
            answer = "0" + answer
        
        return answer[:3]  # Ensure exactly 3 digits