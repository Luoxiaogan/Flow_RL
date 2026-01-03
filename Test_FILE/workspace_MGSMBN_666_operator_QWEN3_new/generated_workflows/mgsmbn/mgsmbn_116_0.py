# Workflow ID: mgsmbn_116_0
# Benchmark: mgsmbn
# Data Indices: [187]

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

        # Step 1: Generate multiple parallel interpretations of the problem
        interpretation_instructions = [
            """Analyze the Bengali problem text and extract:
            - All named entities (people, objects, places) and their roles
            - All numerical values and what they represent
            - Actions or events described and their sequence
            - Explicit and implicit mathematical relationships
            - Units of measurement and constraints (e.g., non-negative, integer)
            Format as a structured JSON-like object with keys: entities, values, relationships, constraints, target.""",
            
            """Focus specifically on numerical relationships:
            - Identify all quantities and their modifiers (half, double, more than, etc.)
            - Map linguistic phrases to mathematical operations
            - Identify what is being asked (target variable)
            - Note any proportional, sequential, or comparative relationships
            Format as a structured JSON-like object with keys: quantities, operations, target, dependencies.""",
            
            """Focus on real-world plausibility and constraints:
            - What are the physical or logical constraints? (e.g., can't have negative apples)
            - Are there any implicit assumptions? (e.g., people must be whole numbers)
            - What is the expected answer type? (integer, decimal, unit)
            - What would constitute an obviously wrong answer?
            Format as a structured JSON-like object with keys: constraints, assumptions, answer_format, sanity_checks."""
        ]

        interpretations = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in interpretation_instructions]
        )

        # Step 2: Ensemble the interpretations into a unified problem representation
        unified_representation = await self.ensemble(
            instruction="""Synthesize the three interpretations into a single, coherent problem representation.
            Resolve conflicts by:
            - Preferring interpretations that maintain unit consistency
            - Choosing the most complete set of entities and relationships
            - Enforcing real-world plausibility (no negative quantities unless explicitly allowed)
            - Preserving all mathematical relationships
            Format as a comprehensive JSON-like structure with all keys from the inputs, merged and deconflicted.""",
            contexts_list=interpretations
        )

        # Step 3: Decompose the problem into ordered subproblems
        decomposition = await self.decompose(
            instruction="""Break down the problem into minimal, sequentially dependent computational steps.
            Each subproblem should:
            - Be solvable with basic arithmetic or simple algebra
            - Have clearly defined inputs and outputs
            - Specify units and validation constraints (e.g., >0, integer)
            - List dependencies (which previous steps it relies on)
            Return as a list of subproblems with 'id', 'description', 'dependencies', and 'validation_rules'.""",
            context=unified_representation
        )

        # Step 4: Execute each subproblem with validation and potential retry
        results = {}
        for step in decomposition:
            step_id = step['id']
            dependencies = step.get('dependencies', '').split(',') if step.get('dependencies') else []
            
            # Wait for dependencies to complete
            dep_results = {dep_id: results[dep_id] for dep_id in dependencies if dep_id in results}
            
            # Build context from dependencies
            dep_context = "\n".join([f"Step {dep_id}: {results[dep_id]}" for dep_id in dependencies if dep_id in results])
            
            # Define validation rules from step
            validation_rules = step.get('validation_rules', 'Result should be a number')
            
            # Attempt computation with retry loop
            for attempt in range(3):
                try:
                    # Generate code to solve this subproblem
                    code_result = await self.programmer(
                        instruction=f"""Solve this subproblem:
                        {step['description']}
                        
                        Context from previous steps:
                        {dep_context}
                        
                        Validation rules: {validation_rules}
                        
                        Write Python code that computes the answer. Return only the numerical result.""",
                        context=unified_representation,
                        max_retries=1
                    )
                    
                    # Extract numerical result from code output
                    # Look for the last line that looks like a number
                    lines = code_result.strip().split('\n')
                    numerical_result = None
                    for line in reversed(lines):
                        try:
                            # Try to parse as float
                            numerical_result = float(line.strip())
                            break
                        except ValueError:
                            continue
                    
                    if numerical_result is None:
                        raise ValueError("No numerical result found in code output")
                    
                    # Validate the result
                    validation_feedback = await self.generate(
                        instruction=f"""Validate this result for subproblem {step_id}:
                        Result: {numerical_result}
                        Validation rules: {validation_rules}
                        Context: {step['description']}
                        
                        Is this result valid? If not, explain why and suggest correction.
                        Respond with 'VALID' if acceptable, or 'INVALID: [reason]' if not.""",
                        context=code_result
                    )
                    
                    if "VALID" in validation_feedback:
                        results[step_id] = numerical_result
                        break
                    else:
                        if attempt == 2:  # Last attempt
                            results[step_id] = numerical_result  # Use anyway, but note issue
                        # Otherwise, retry with feedback
                        continue
                        
                except Exception as e:
                    if attempt == 2:
                        # Final fallback: use generate to estimate
                        fallback_result = await self.generate(
                            instruction=f"""Given this subproblem failed computation:
                            {step['description']}
                            Previous attempts failed with: {str(e)}
                            
                            Provide your best estimate of the numerical answer based on reasoning.
                            Return only the number.""",
                            context=unified_representation
                        )
                        try:
                            results[step_id] = float(fallback_result.strip())
                        except:
                            results[step_id] = 0.0  # Ultimate fallback
                        break

        # Step 5: Get final answer (last step or explicitly identified target)
        final_step_id = decomposition[-1]['id'] if decomposition else "unknown"
        final_answer = results.get(final_step_id, 0.0)
        
        # Step 6: Final sanity check
        sanity_check = await self.generate(
            instruction=f"""Perform final validation of the answer:
            Problem: {self.problem_text}
            Computed answer: {final_answer}
            Unified representation: {unified_representation}
            
            Check:
            - Does this answer make sense in context?
            - Does it satisfy all constraints mentioned?
            - Is it in the expected format (integer/decimal)?
            - Is it within a plausible range?
            
            If the answer seems incorrect, provide a corrected numerical answer.
            Otherwise, return the same number.
            Return ONLY the final numerical answer, nothing else.""",
            context=str(results)
        )
        
        # Extract final number from sanity check
        try:
            final_answer = float(sanity_check.strip())
        except:
            pass  # Keep previous answer if parsing fails
        
        return final_answer