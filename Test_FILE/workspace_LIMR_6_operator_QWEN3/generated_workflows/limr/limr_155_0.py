# Workflow ID: limr_155_0
# Benchmark: limr
# Data Indices: [240, 341]

import asyncio

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

        # Step 1: Deep problem classification to determine solution strategies
        classification = await self.generate(
            instruction="""Perform a deep semantic classification of this mathematical problem. Analyze:
            1. Primary mathematical domain (algebra, geometry, combinatorics, number theory, calculus, etc.)
            2. Key mathematical objects involved (functions, sets, inequalities, sequences, geometric figures, etc.)
            3. Required operations (optimization, counting, proof, transformation, solving equations, etc.)
            4. Structural properties (symmetry, recursion, constraints, boundary conditions, etc.)
            5. Expected answer format and precision requirements
            6. Potential solution strategies ranked by likely effectiveness
            Output a structured JSON-like analysis with clear sections.""",
            context=""
        )

        # Step 2: Generate dynamic parallel solution tracks based on classification
        # Create 3-5 specialized reasoning tracks tailored to the problem type
        track_instructions = [
            """Adopt an ALGEBRAIC/ANALYTIC perspective: 
            - Translate the problem into equations, inequalities, or functional relationships
            - Apply algebraic manipulations, substitutions, or transformations
            - Consider case analysis, domain restrictions, or parameter variations
            - Derive step-by-step symbolic solution with clear justification""",
            
            """Adopt a GEOMETRIC/VISUAL perspective:
            - Interpret the problem geometrically (even if not explicitly geometric)
            - Use coordinate systems, vectors, or transformations if applicable
            - Consider symmetry, invariants, or extremal principles
            - Sketch conceptual diagrams or graphs to guide reasoning""",
            
            """Adopt a COMPUTATIONAL/ALGORITHMIC perspective:
            - Identify discrete states, transitions, or recursive relationships
            - Formulate as an algorithm, simulation, or iterative process
            - Consider edge cases, boundary conditions, and termination criteria
            - Prepare for potential code implementation of key computational steps""",
            
            """Adopt a COMBINATORIAL/PROBABILISTIC perspective:
            - If applicable, model as counting problem, probability space, or combinatorial structure
            - Apply counting principles, expected value, or probabilistic reasoning
            - Consider complementary counting, symmetry, or generating functions
            - Verify with small cases or simulation""",
            
            """Adopt an ADVANCED/CREATIVE perspective:
            - Look for non-obvious insights, clever substitutions, or elegant transformations
            - Consider proof by contradiction, induction, or invariant arguments
            - Explore connections to deeper mathematical concepts or theorems
            - Challenge assumptions and consider alternative interpretations"""
        ]

        # Generate parallel solution attempts
        solution_tracks = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on the problem classification: {classification}
                
                {track_instruction}
                
                Develop a complete, step-by-step solution attempt. Show all reasoning, calculations, and justifications. 
                If you reach a computational bottleneck, clearly identify what needs to be computed and how.
                Your solution should be self-contained and rigorous.""",
                context=""
            ) for track_instruction in track_instructions]
        )

        # Step 3: For each solution track, identify computational kernels for programmer
        computational_tasks = []
        for i, track in enumerate(solution_tracks):
            computational_analysis = await self.generate(
                instruction=f"""Analyze this solution track for computational components:
                - Identify specific calculations, equation solving, or simulations needed
                - Extract precise mathematical expressions or algorithms to compute
                - Specify required precision and format of output
                - If no computation needed, state "NONE"
                
                Solution Track {i+1}:
                {track}""",
                context=track
            )
            
            if "NONE" not in computational_analysis.upper():
                try:
                    computation_result = await self.programmer(
                        instruction=f"""Execute the following computational task from solution track {i+1}:
                        {computational_analysis}
                        
                        Provide exact results with full precision. Show the code used and its output.
                        If multiple computations are needed, perform them sequentially.""",
                        context=computational_analysis,
                        max_retries=3
                    )
                    # Revise the original track with computational results
                    revised_track = await self.revise(
                        instruction=f"""Incorporate the following computational results into the solution:
                        {computation_result}
                        
                        Update all relevant steps, calculations, and conclusions. Ensure consistency and precision.""",
                        context=track
                    )
                    computational_tasks.append(revised_track)
                except Exception as e:
                    # If computation fails, keep original track
                    computational_tasks.append(track)
            else:
                computational_tasks.append(track)

        # Step 4: Ensemble synthesis with critical verification
        final_solution = await self.ensemble(
            instruction="""Critically evaluate and synthesize these solution attempts:
            1. Compare logical consistency, completeness, and adherence to problem constraints
            2. Verify computational accuracy and mathematical rigor
            3. Identify points of agreement and disagreement between solutions
            4. Resolve conflicts by preferring solutions with clearer derivations and better verification
            5. Synthesize the most robust elements into a single coherent solution
            6. Ensure all steps are justified and no assumptions are unverified
            
            Output a complete, polished solution with clear step-by-step reasoning.""",
            contexts_list=computational_tasks
        )

        # Step 5: Adversarial critique and refinement loop
        for refinement_round in range(3):
            critique = await self.generate(
                instruction=f"""Adversarial critique of this solution:
                - Assume this solution contains at least one significant error
                - Identify the most likely point of failure (algebraic error, missed case, invalid assumption, etc.)
                - Test edge cases, boundary conditions, and special values
                - Verify dimensional consistency, modular constraints, or other domain-specific checks
                - Suggest specific improvements or corrections
                
                Solution to critique:
                {final_solution}""",
                context=final_solution
            )
            
            # Check if critique found serious issues
            if any(phrase in critique.lower() for phrase in ["error", "mistake", "incorrect", "flaw", "problem", "issue", "contradiction"]):
                final_solution = await self.revise(
                    instruction=f"""Address the following critique:
                    {critique}
                    
                    Revise the solution to fix identified issues. Strengthen weak points and add additional verification.
                    Maintain all correct elements while improving problematic areas.""",
                    context=final_solution
                )
            else:
                break  # No serious issues found, exit refinement loop

        # Step 6: Final answer extraction and formatting
        final_answer = await self.revise(
            instruction="""Extract and format the final answer according to LIMR requirements:
            - The answer must be an integer between 000 and 999
            - If the solution produces a fraction, compute its exact decimal value and convert appropriately
            - If symbolic, evaluate numerically with exact precision
            - Justify the conversion process and show the final integer answer clearly
            - Format as: "FINAL ANSWER: XXX" where XXX is the three-digit integer
            
            Ensure absolute precision - no approximations or rounding unless explicitly permitted by the problem.""",
            context=final_solution
        )

        return final_answer