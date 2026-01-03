# Workflow ID: mgsmbn_21_0
# Benchmark: mgsmbn
# Data Indices: [63, 90]

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
        
        # Step 1: Initial problem analysis and classification
        initial_analysis = await self.generate(
            instruction="""Perform comprehensive problem analysis:
            1. Extract all named entities (people, objects) and their roles
            2. Identify all numerical values and their contextual meaning (units, quantities)
            3. Map relationships between entities (comparisons, dependencies, sequences)
            4. Detect implicit constraints (real-world limits, unit consistency, integer requirements)
            5. Classify problem type: 
               - Simple arithmetic (single operation)
               - Multi-step sequential (ordered operations)
               - Conditional (if-then scenarios)
               - Proportional (ratios, percentages)
               - Multi-entity (multiple actors with different quantities)
            6. Flag any ambiguous phrasing that needs disambiguation
            7. Predict potential error points (unit conversions, order of operations, boundary conditions)
            
            Format output as structured sections with clear headings.""",
            context=""
        )

        # Step 2: Problem type classification for adaptive routing
        problem_type = await self.generate(
            instruction=f"""Based on the following analysis, classify this problem into one of three complexity tiers:
            Analysis: {initial_analysis}
            
            TIER 1 (Simple): Single operation, no dependencies, no ambiguity
            TIER 2 (Moderate): Multiple steps with clear sequence, no ambiguity
            TIER 3 (Complex): Ambiguous phrasing, conditional logic, or interdependent calculations
            
            Also identify the primary mathematical operation needed (addition, subtraction, multiplication, division, proportion, etc.)
            Return ONLY the tier number (1, 2, or 3) and primary operation, comma separated.""",
            context=initial_analysis
        )
        
        tier = problem_type.split(',')[0].strip()
        primary_operation = problem_type.split(',')[1].strip() if ',' in problem_type else "unknown"

        # Step 3: Adaptive workflow routing based on complexity tier
        if tier == "1":
            # Simple path: direct calculation
            solution_attempt = await self.programmer(
                instruction=f"""Solve this problem directly using {primary_operation}:
                - Extract numbers and their meanings from context
                - Apply single mathematical operation
                - Return only the numerical result
                - Validate against real-world constraints (no negative quantities, appropriate units)""",
                context=initial_analysis
            )
            
        elif tier == "2":
            # Moderate path: decompose then calculate
            decomposition = await self.decompose(
                instruction=f"""Break this problem into sequential subproblems:
                - Each subproblem should represent one clear mathematical step
                - Specify dependencies between steps (which calculations must come first)
                - Include units and real-world constraints for each step
                - Ensure the final step produces the required answer
                Base decomposition on this analysis: {initial_analysis}""",
                context=initial_analysis
            )
            
            # Execute subproblems in dependency order
            solution_steps = {}
            max_dependency_depth = max([len(step.get('dependencies', '').split(',')) if step.get('dependencies') else 0 for step in decomposition])
            
            for depth in range(max_dependency_depth + 1):
                current_depth_steps = [step for step in decomposition if len(step.get('dependencies', '').split(',')) == depth]
                
                if not current_depth_steps:
                    continue
                    
                # Prepare context for this depth level
                dependency_context = "\n".join([f"Step {dep_id}: {solution_steps.get(dep_id, 'Not calculated yet')}" 
                                              for step in current_depth_steps 
                                              for dep_id in step.get('dependencies', '').split(',') if dep_id])
                
                # Execute current depth steps in parallel
                tasks = []
                for step in current_depth_steps:
                    step_id = step['id']
                    step_instruction = f"""Solve this subproblem: {step['description']}
                    Context from previous steps: {dependency_context}
                    Original problem context: {initial_analysis}
                    Return ONLY the numerical result for this step."""
                    
                    task = self.programmer(instruction=step_instruction, context=dependency_context)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                
                # Store results by step ID
                for i, step in enumerate(current_depth_steps):
                    solution_steps[step['id']] = results[i]
            
            # Extract final answer (last step or step marked as final)
            final_step = decomposition[-1]  # Assume last step is final
            solution_attempt = solution_steps.get(final_step['id'], "Error: Final step not calculated")
            
        else:  # Tier 3 - Complex path with multiple perspectives and verification
            # Generate multiple solution perspectives
            perspectives = await asyncio.gather(
                self.generate(instruction=f"""Solve this problem from ALGEBRAIC perspective:
                - Define variables for unknowns
                - Write equations based on relationships
                - Solve systematically
                - Show all steps
                Context: {initial_analysis}""", context=initial_analysis),
                
                self.generate(instruction=f"""Solve this problem from ARITHMETIC perspective:
                - Break into sequential calculations
                - Show intermediate results
                - Track units throughout
                - Verify each step makes sense
                Context: {initial_analysis}""", context=initial_analysis),
                
                self.generate(instruction=f"""Solve this problem from REAL-WORLD perspective:
                - Imagine the physical scenario
                - What would actually happen?
                - Are there practical constraints?
                - Does the answer make sense in reality?
                Context: {initial_analysis}""", context=initial_analysis)
            )
            
            # Synthesize perspectives
            synthesized_solution = await self.ensemble(
                instruction="""Synthesize the three perspectives into one coherent solution:
                - Resolve any contradictions between approaches
                - Combine the most reliable elements from each
                - Ensure mathematical accuracy and real-world plausibility
                - Produce a step-by-step solution that leads to a single numerical answer
                - The final output should be ONLY the numerical answer, nothing else""",
                contexts_list=perspectives
            )
            
            # Verify and refine
            solution_attempt = await self.revise(
                instruction="""Verify this solution:
                - Does the number make sense in context? (e.g., no negative people, reasonable weights)
                - Are units consistent throughout?
                - Were all conditions in the problem satisfied?
                - Is the calculation mathematically sound?
                If any issues, correct them and return only the final numerical answer.
                If no issues, return the answer unchanged.""",
                context=synthesized_solution
            )

        # Final extraction and cleanup - ensure we return only a clean number
        final_answer = await self.generate(
            instruction="""Extract ONLY the numerical answer from the following text.
            Remove any units, explanations, or additional text.
            If multiple numbers are present, select the one that answers the original question.
            Return ONLY the number, nothing else.""",
            context=solution_attempt
        )
        
        # Clean the answer (remove any remaining non-numeric characters except decimal point)
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer)
        
        return cleaned_answer