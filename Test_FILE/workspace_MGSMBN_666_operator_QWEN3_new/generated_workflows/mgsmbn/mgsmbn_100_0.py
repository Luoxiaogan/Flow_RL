# Workflow ID: mgsmbn_100_0
# Benchmark: mgsmbn
# Data Indices: [154, 158]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
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
        """
        Universal workflow for MGSM Bengali math problems.
        Architecture: State Machine Extraction → Parallel Analysis → Ensemble Synthesis → Code Execution → Validation Loop
        """
        import asyncio
        import re
        
        # Stage 1: Comprehensive Problem Decomposition
        decomposition_instruction = """
        Systematically decompose this Bengali math problem into its fundamental components. Identify:
        1. All entities (people, objects, quantities) with their initial values
        2. All operations (additions, subtractions, multiplications, divisions) with timing/conditions
        3. All constraints (non-negative, integer-only, unit consistency)
        4. The final query (what is being asked)
        5. Any hidden steps or implicit assumptions
        
        Structure your response as:
        ENTITIES:
        - [Entity Name]: [Initial Value] [Units] [Description]
        
        OPERATIONS (in chronological order):
        - Step [N]: [Operation] on [Entity] by [Amount] [Condition/Time]
        
        CONSTRAINTS:
        - [Constraint Description]
        
        QUERY:
        - [What needs to be calculated]
        
        HIDDEN ASSUMPTIONS:
        - [Any implicit information]
        """
        
        decomposition = await self.generate(
            instruction=decomposition_instruction,
            context=""
        )
        
        # Stage 2: Parallel Analysis from Multiple Perspectives
        perspective_tasks = [
            self.generate(
                instruction=f"""
                Analyze this problem from a PURELY MATHEMATICAL perspective:
                - Convert all operations into formal mathematical expressions
                - Identify the sequence of calculations needed
                - Note any algebraic relationships or equations
                - Suggest the most efficient computational approach
                
                Use the decomposition as context:
                {decomposition}
                """,
                context=decomposition
            ),
            self.generate(
                instruction=f"""
                Analyze this problem from a REAL-WORLD CONTEXT perspective:
                - What are the practical constraints? (e.g., can't have negative trees, fractional people)
                - Are there any unit conversions needed?
                - Does the scenario suggest any implicit constraints?
                - How would this play out in reality?
                
                Use the decomposition as context:
                {decomposition}
                """,
                context=decomposition
            ),
            self.generate(
                instruction=f"""
                Analyze this problem from a STEP-BY-STEP EXECUTION perspective:
                - Create a detailed timeline of events
                - For each step, specify exactly what changes and how
                - Track cumulative effects
                - Identify potential error points in calculation
                
                Use the decomposition as context:
                {decomposition}
                """,
                context=decomposition
            )
        ]
        
        mathematical_analysis, context_analysis, execution_analysis = await asyncio.gather(*perspective_tasks)
        
        # Stage 3: Ensemble Synthesis into Unified Computational Model
        synthesis_instruction = """
        Synthesize the three analyses into a single, coherent computational model:
        1. Combine the mathematical formalism with real-world constraints
        2. Create a step-by-step execution plan that respects the timeline
        3. Resolve any conflicts between perspectives
        4. Format as a clear sequence of operations with explicit inputs and outputs
        
        Structure your response as:
        COMPUTATIONAL MODEL:
        - Initial State: [List all initial values]
        - Step 1: [Operation] → [Result]
        - Step 2: [Operation] → [Result]
        - ...
        - Final Calculation: [How to derive the answer]
        
        CONSTRAINTS TO ENFORCE:
        - [List all constraints that must be checked]
        """
        
        synthesized_model = await self.ensemble(
            instruction=synthesis_instruction,
            contexts_list=[mathematical_analysis, context_analysis, execution_analysis]
        )
        
        # Stage 4: Generate and Execute Code
        code_instruction = f"""
        Generate Python code that implements the computational model exactly as specified.
        Requirements:
        - Use only basic arithmetic operations (+, -, *, /, //, %)
        - Include detailed comments explaining each step
        - Initialize all variables with their starting values
        - Follow the exact sequence of operations from the model
        - Include assertions to check constraints after each critical step
        - The final answer must be stored in a variable called 'final_answer'
        - Print only the final_answer (no other output)
        
        Computational Model:
        {synthesized_model}
        
        IMPORTANT: The code must handle all edge cases mentioned in constraints.
        If any constraint is violated during execution, raise an exception with a descriptive message.
        """
        
        code_result = await self.programmer(
            instruction=code_instruction,
            context=synthesized_model
        )
        
        # Stage 5: Validation and Revision Loop
        validation_instruction = f"""
        Validate the solution against the original problem:
        1. Does the final answer make sense in context? (e.g., no negative quantities when impossible)
        2. Are all units consistent throughout?
        3. Does it satisfy all constraints identified in decomposition?
        4. Is the calculation sequence logically sound?
        5. Are there any arithmetic errors?
        
        If any issues are found, specify exactly what needs to be fixed.
        If no issues, respond with "VALID: [final answer]".
        
        Original Decomposition:
        {decomposition}
        
        Computational Model:
        {synthesized_model}
        
        Code Result:
        {code_result}
        """
        
        validation = await self.generate(
            instruction=validation_instruction,
            context=code_result
        )
        
        # Conditional revision loop
        final_answer = None
        max_retries = 3
        current_attempt = 0
        
        while current_attempt < max_retries:
            if "VALID:" in validation:
                # Extract final answer
                match = re.search(r'VALID:\s*([0-9]+\.?[0-9]*)', validation)
                if match:
                    final_answer = match.group(1)
                    break
            else:
                # Revise based on validation feedback
                revision_instruction = f"""
                Revise the computational model and code based on the validation feedback:
                - Address all issues identified in validation
                - Maintain all correct aspects of the previous solution
                - Ensure the revised solution satisfies all constraints
                - Keep the same output format (final_answer variable)
                
                Validation Feedback:
                {validation}
                
                Previous Computational Model:
                {synthesized_model}
                
                Previous Code Result:
                {code_result}
                """
                
                revised_model = await self.revise(
                    instruction=revision_instruction,
                    context=synthesized_model
                )
                
                # Generate new code
                revised_code_instruction = f"""
                Generate Python code implementing the revised computational model.
                Follow all previous requirements, plus address the validation issues.
                
                Revised Computational Model:
                {revised_model}
                """
                
                code_result = await self.programmer(
                    instruction=revised_code_instruction,
                    context=revised_model
                )
                
                # Re-validate
                validation = await self.generate(
                    instruction=validation_instruction,
                    context=code_result
                )
                
                synthesized_model = revised_model  # Update for next iteration if needed
                current_attempt += 1
        
        # Final extraction and return
        if final_answer is None:
            # Fallback: extract from code result if validation loop failed
            match = re.search(r'final_answer\s*=\s*([0-9]+\.?[0-9]*)', code_result)
            if match:
                final_answer = match.group(1)
            else:
                # Last resort: return first number found
                numbers = re.findall(r'[0-9]+\.?[0-9]*', code_result)
                final_answer = numbers[0] if numbers else "0"
        
        return final_answer