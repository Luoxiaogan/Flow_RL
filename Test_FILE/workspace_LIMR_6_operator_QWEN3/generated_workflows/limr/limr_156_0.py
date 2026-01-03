# Workflow ID: limr_156_0
# Benchmark: limr
# Data Indices: [189, 230]

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

        # STEP 1: Deep Structural Classification
        classification = await self.generate(
            instruction="""Perform a comprehensive classification of this mathematical problem. Address:
            1. Primary domain (algebra, geometry, combinatorics, number theory, etc.)
            2. Secondary domains or cross-domain elements
            3. Problem type: proof, optimization, counting, equation solving, etc.
            4. Key mathematical objects involved (functions, shapes, sequences, etc.)
            5. Required techniques (induction, modular arithmetic, coordinate geometry, etc.)
            6. Expected answer format and constraints (integer 000-999, exact value, etc.)
            7. Potential pitfalls or non-obvious insights
            8. Suggested solution strategies (at least 3 distinct approaches)
            
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # STEP 2: Generate Multiple Decomposition Strategies
        decomposition_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a decomposition strategy focusing on ALGEBRAIC/ANALYTIC approach:
                - Break problem into minimal subproblems
                - Specify dependencies between subproblems
                - Identify which subproblems require symbolic manipulation
                - Which require numerical computation
                - Highlight potential algebraic simplifications or substitutions""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a decomposition strategy focusing on GEOMETRIC/VISUAL approach:
                - Break problem into spatial or visual components
                - Identify diagrams, coordinates, or transformations needed
                - Specify how geometric properties (symmetry, congruence, etc.) can be leveraged
                - Highlight potential coordinate system choices""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a decomposition strategy focusing on COMBINATORIAL/PROBABILISTIC approach:
                - Break problem into counting or probability subproblems
                - Identify sample spaces, events, or combinatorial structures
                - Specify when to use permutations, combinations, or generating functions
                - Highlight potential overcounting issues or symmetry arguments""",
                context=""
            )
        )

        # STEP 3: Convert Strategies to Formal Decompositions
        decompositions = await asyncio.gather(
            *[self.decompose(
                instruction=f"""Convert the following strategy into a formal decomposition with explicit subproblems and dependencies:
                Strategy: {strategy}
                
                Requirements:
                - Each subproblem must be self-contained and solvable in isolation (given dependencies)
                - Dependencies must be explicitly listed by ID
                - Include at least one computational subproblem suitable for code generation
                - Include at least one proof/verification subproblem
                - Ensure the final subproblem produces the required answer format (integer 000-999)""",
                context=""
            ) for strategy in decomposition_strategies]
        )

        # STEP 4: Parallel Solution Threads
        async def solve_decomposition(decomp, strategy_name):
            """Solve a single decomposition thread with verification at each step"""
            results = {}
            # Solve subproblems in dependency order
            for subproblem in decomp:
                sub_id = subproblem['id']
                deps = subproblem['dependencies'].split(',') if subproblem['dependencies'] else []
                
                # Wait for dependencies
                dep_context = "\n".join([f"Subproblem {did}: {results[did]}" for did in deps if did in results])
                
                # Generate initial solution
                solution = await self.generate(
                    instruction=f"""Solve this subproblem as part of the {strategy_name} approach:
                    {subproblem['description']}
                    
                    Context from dependencies:
                    {dep_context}
                    
                    Requirements:
                    - Show all steps clearly
                    - Justify key insights
                    - If computational, provide exact expressions
                    - If proof-based, state assumptions and logical flow
                    - Flag any uncertainties or alternative interpretations""",
                    context=dep_context
                )
                
                # Verify and revise
                for _ in range(2):  # Up to 2 revision cycles
                    verification = await self.generate(
                        instruction=f"""Critically verify this solution:
                        {solution}
                        
                        Check for:
                        1. Logical consistency
                        2. Mathematical accuracy
                        3. Adherence to problem constraints
                        4. Potential calculation errors
                        5. Alternative approaches that might be simpler
                        
                        If errors found, specify exactly what needs revision.""",
                        context=solution
                    )
                    
                    if "error" not in verification.lower() and "incorrect" not in verification.lower() and "flaw" not in verification.lower():
                        break
                    
                    solution = await self.revise(
                        instruction=f"""Revise based on this feedback:
                        {verification}
                        
                        Improve:
                        - Fix identified errors
                        - Strengthen weak arguments
                        - Add missing steps
                        - Clarify ambiguous statements""",
                        context=solution
                    )
                
                # If computational, generate and execute code
                if any(keyword in subproblem['description'].lower() for keyword in ['calculate', 'compute', 'numerical', 'value']):
                    try:
                        code_result = await self.programmer(
                            instruction=f"""Generate Python code to compute the exact value for:
                            {subproblem['description']}
                            
                            Based on this reasoning:
                            {solution}
                            
                            Requirements:
                            - Use exact arithmetic (fractions, sympy if needed)
                            - Output must be integer between 000-999
                            - Include verification steps in code
                            - Handle edge cases""",
                            context=solution,
                            max_retries=3
                        )
                        solution = f"{solution}\n\nPROGRAMMER VERIFICATION:\n{code_result}"
                    except Exception as e:
                        # Fallback: keep original solution
                        pass
                
                results[sub_id] = solution
            
            # Synthesize final answer from last subproblem
            final_sub_id = decomp[-1]['id'] if decomp else ""
            final_answer = results.get(final_sub_id, "No final answer generated")
            
            return {
                "strategy": strategy_name,
                "solution": final_answer,
                "intermediate_results": results,
                "decomposition": decomp
            }

        # Execute all decomposition threads in parallel
        strategy_names = ["Algebraic/Analytic", "Geometric/Visual", "Combinatorial/Probabilistic"]
        solution_threads = await asyncio.gather(
            *[solve_decomposition(decomp, name) for decomp, name in zip(decompositions, strategy_names)]
        )

        # STEP 5: Meta-Analysis and Synthesis
        meta_analysis = await self.generate(
            instruction=f"""Perform meta-analysis of these solution attempts:
            {[thread['strategy'] for thread in solution_threads]}
            
            For each thread:
            1. Assess completeness and correctness
            2. Identify strengths and weaknesses
            3. Note any contradictions between threads
            4. Highlight novel insights from each approach
            5. Recommend which thread(s) to trust for final answer
            
            Then propose a synthesis strategy that combines the best elements from multiple threads.""",
            context="\n\n".join([f"THREAD {thread['strategy']}:\n{thread['solution']}" for thread in solution_threads])
        )

        # STEP 6: Generate Final Synthesized Solution
        final_solutions = [thread['solution'] for thread in solution_threads]
        synthesized_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer from these solution threads:
            {meta_analysis}
            
            Requirements:
            1. Resolve any contradictions between threads
            2. Combine complementary insights
            3. Ensure final answer is an integer between 000-999
            4. Provide clear justification for the chosen answer
            5. Include verification from at least two independent approaches
            
            Format:
            FINAL ANSWER: [integer]
            JUSTIFICATION: [concise reasoning]
            VERIFICATION: [cross-check from alternative method]""",
            contexts_list=final_solutions
        )

        # STEP 7: Final Verification and Formatting
        final_output = await self.revise(
            instruction="""Extract the final integer answer (000-999) and format it properly.
            Ensure:
            - Answer is exactly three digits (pad with leading zeros if needed)
            - No units or additional text
            - Answer is mathematically justified in the reasoning
            - If multiple candidates exist, select the one with strongest verification
            
            If answer cannot be confidently determined, return "000" as fallback.""",
            context=synthesized_answer
        )

        # Extract just the three-digit answer
        import re
        match = re.search(r'\b(\d{3})\b', final_output)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and format to 3 digits
            numbers = re.findall(r'\d+', final_output)
            if numbers:
                return f"{int(numbers[0]) % 1000:03d}"
            else:
                return "000"