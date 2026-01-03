# Workflow ID: mgsmbn_9_0
# Benchmark: mgsmbn
# Data Indices: [43, 49]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Phase 1: Parallel Problem Deconstruction
        entity_extraction = self.generate(
            instruction="""Extract all mathematical entities from the Bengali problem:
            - List every number with its unit (টাকা, জন, ঘণ্টা, etc.) and contextual meaning
            - Identify all operations implied by verbs (যোগ করেছিল, বিভক্ত করেছিল, বাড়িয়েছিল)
            - Map relationships: what depends on what? (e.g., "25% of total bill")
            - Flag any ambiguous phrases that could have multiple interpretations
            Format as bullet points with clear labels.""",
            context=""
        )
        
        narrative_extraction = self.generate(
            instruction="""Deconstruct the narrative structure:
            - What is the chronological sequence of events?
            - Who are the actors and what actions do they perform?
            - What is the explicit question being asked?
            - Are there implicit constraints (e.g., "people" implies integer counts)?
            Format as a timeline with actor-action-object triples.""",
            context=""
        )
        
        constraint_extraction = self.generate(
            instruction="""Identify all constraints and validity conditions:
            - What makes an answer invalid? (e.g., negative money, fractional people)
            - What units must the final answer have?
            - Are there boundary conditions? (minimum/maximum values)
            - What real-world rules apply? (e.g., fees can't exceed 100%)
            Format as a list of "MUST" and "MUST NOT" statements.""",
            context=""
        )
        
        # Execute parallel extraction
        entity_result, narrative_result, constraint_result = await asyncio.gather(
            entity_extraction, narrative_extraction, constraint_extraction
        )

        # Phase 2: Strategy Synthesis via Ensemble
        problem_model = await self.ensemble(
            instruction="""Synthesize a unified mathematical model from the three analyses:
            1. Integrate entities, narrative, and constraints into one coherent structure
            2. Resolve conflicts by prioritizing: mathematical consistency > narrative flow > linguistic ambiguity
            3. Explicitly define: knowns, unknowns, operations sequence, and validation rules
            4. Output as a formal problem statement with variables and equations if applicable
            5. If any ambiguity remains, state it explicitly as a question to be resolved""",
            contexts_list=[entity_result, narrative_result, constraint_result]
        )

        # Phase 3: Multi-Strategy Solution Generation (Parallel)
        direct_approach = self.generate(
            instruction=f"""Solve using direct arithmetic:
            - Follow the chronological/logical sequence from the narrative
            - Show each calculation step with intermediate results
            - Track units at every step (টাকা, জন, etc.)
            - Verify against constraints after each operation
            Problem Model: {problem_model}""",
            context=problem_model
        )
        
        algebraic_approach = self.generate(
            instruction=f"""Solve using algebraic formulation:
            - Define variables for unknowns
            - Set up equations based on relationships
            - Solve step-by-step, showing substitutions
            - Verify solution satisfies all constraints
            Problem Model: {problem_model}""",
            context=problem_model
        )
        
        simulation_approach = self.generate(
            instruction=f"""Solve by simulating the real-world process:
            - Imagine physically performing the actions described
            - Track state changes (e.g., money in wallet, items in basket)
            - Use unit annotations to prevent category errors
            - Stop when you reach the asked quantity
            Problem Model: {problem_model}""",
            context=problem_model
        )
        
        # Execute parallel solution attempts
        direct_sol, algebraic_sol, simulation_sol = await asyncio.gather(
            direct_approach, algebraic_approach, simulation_approach
        )

        # Phase 4: Adversarial Validation Loop
        candidate_solutions = [direct_sol, algebraic_sol, simulation_sol]
        best_solution = None
        critique = ""
        
        for iteration in range(3):  # Max 3 refinement rounds
            # Ensemble selects most promising solution
            current_best = await self.ensemble(
                instruction=f"""Select the most robust solution:
                - Prioritize solutions that explicitly show unit tracking
                - Favor solutions that address edge cases
                - Prefer solutions with clear step-by-step verification
                - If all are flawed, pick the one easiest to fix
                Previous critique (if any): {critique}""",
                contexts_list=candidate_solutions
            )
            
            # Adversarial critique
            critique = await self.revise(
                instruction=f"""Act as a skeptical examiner:
                - Assume this solution is WRONG. What's the most likely error?
                - Test with extreme values (zero, negative, very large numbers)
                - Check unit consistency at every step
                - Verify against all constraints from Phase 1
                - If no significant flaws, respond with 'VALID'
                Solution to critique: {current_best}""",
                context=current_best
            )
            
            if "VALID" in critique.upper():
                best_solution = current_best
                break
            else:
                # Generate defense/correction
                best_solution = await self.generate(
                    instruction=f"""Defend or correct the solution against this critique:
                    - If the critique is valid, modify the solution to fix the flaw
                    - If the critique is invalid, explain why with mathematical reasoning
                    - Maintain all previous verification steps
                    - Output the corrected/defended solution in full
                    Critique: {critique}
                    Original Solution: {current_best}""",
                    context=f"{current_best}\n\nCRITIQUE: {critique}"
                )
                candidate_solutions = [best_solution]  # Reset candidates after correction

        if best_solution is None:
            best_solution = current_best  # Fallback if loop exhausted

        # Final Extraction: Isolate numerical answer
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution:
            - Remove all units, explanations, and intermediate steps
            - If answer is decimal, preserve exact precision (no rounding unless specified)
            - If multiple numbers appear, select the one that answers the explicit question
            - Output ONLY the number, nothing else
            - Example valid outputs: "48", "57.5", "0"
            Solution: """ + best_solution,
            context=best_solution
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        return cleaned