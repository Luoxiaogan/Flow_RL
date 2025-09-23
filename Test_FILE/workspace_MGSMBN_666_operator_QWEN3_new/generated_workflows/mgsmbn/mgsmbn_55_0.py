# Workflow ID: mgsmbn_55_0
# Benchmark: mgsmbn
# Data Indices: [5]

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

        # Step 1: Parallel problem classification from multiple angles
        classification_instructions = [
            """Analyze this Bengali math problem from a mathematical structure perspective:
            - Identify the core mathematical operation(s) required (addition, subtraction, multiplication, division, proportion, rate, etc.)
            - Determine if it's single-step or multi-step
            - Identify if it involves conditional logic or thresholds
            - Classify problem type: Sequential, Rate, Proportional, Distribution, Comparison, or Multi-entity
            - Output in JSON format with keys: "math_operations", "step_count", "has_conditions", "problem_type"
            """,
            
            """Analyze this Bengali math problem from a linguistic perspective:
            - Extract all numerical values and their associated units (টাকা, ঘণ্টা, জিনিস, etc.)
            - Identify key action verbs that imply mathematical operations (যোগ করা, বিয়োগ করা, গুণ, ভাগ, বেশি, কম, etc.)
            - Flag any ambiguous phrases or potential misinterpretations
            - Output in JSON format with keys: "numbers_with_units", "operation_verbs", "ambiguities"
            """,
            
            """Analyze this Bengali math problem from a real-world context perspective:
            - Identify real-world constraints (non-negative results, integer requirements, physical limitations)
            - Determine if unit conversions are needed
            - Assess if the answer should be rounded or kept as decimal
            - Output in JSON format with keys: "constraints", "unit_conversions", "rounding_required"
            """
        ]

        classifications = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in classification_instructions]
        )

        # Step 2: Ensemble classifications into unified problem specification
        unified_spec = await self.ensemble(
            instruction="""Synthesize the three classification perspectives into a single comprehensive problem specification.
            Combine mathematical structure, linguistic elements, and real-world constraints.
            Output must be a well-structured JSON object with all relevant information for solving the problem.
            Include: problem_type, required_operations, numbers_with_units, constraints, and any special handling instructions.
            Ensure no information is lost in synthesis.""",
            contexts_list=classifications
        )

        # Step 3: Conditional decomposition (only for multi-step problems)
        decomposition = None
        if "multi-step" in unified_spec.lower() or "sequential" in unified_spec.lower() or "multi-entity" in unified_spec.lower():
            decomposition = await self.decompose(
                instruction="""Break down this multi-step Bengali math problem into atomic subproblems.
                Each subproblem should be solvable independently once its dependencies are resolved.
                Include units and constraints for each subproblem.
                Format each subproblem with: id, description, dependencies (comma-separated), required_operation, expected_unit, constraints.""",
                context=unified_spec
            )

        # Step 4: Generate mathematical model specification
        model_spec = await self.generate(
            instruction=f"""Based on the unified problem specification and optional decomposition, create a detailed mathematical model specification.
            Include:
            - All known variables with their values and units
            - Unknown variable(s) to solve for
            - Mathematical relationships between variables (equations, inequalities)
            - Step-by-step computational plan (even if single step)
            - Unit consistency checks required
            - Constraint validations needed
            - Special handling for fractions, decimals, or percentages
            
            If decomposition exists, structure the model according to subproblem dependencies.
            Output in clear, structured format suitable for code generation.""",
            context=unified_spec if not decomposition else f"Unified Spec: {unified_spec}\n\nDecomposition: {json.dumps(decomposition)}"
        )

        # Step 5: Generate and execute code with validation loop
        final_answer = None
        last_error = None
        
        for attempt in range(3):  # Max 3 attempts
            try:
                # Generate code
                code_result = await self.programmer(
                    instruction=f"""Generate Python code to solve this Bengali math problem based on the mathematical model specification.
                    Requirements:
                    - Include all necessary calculations with proper order of operations
                    - Handle units appropriately (though final answer is unitless number)
                    - Apply all specified constraints (non-negative, integer if required, etc.)
                    - Include assertions for critical constraints
                    - Return only the final numerical answer (int or float)
                    - Add detailed comments explaining each step in English
                    
                    Model Specification:
                    {model_spec}""",
                    context=model_spec,
                    max_retries=1
                )
                
                # Extract numerical answer from code result
                # Look for the final answer in the output
                lines = code_result.split('\n')
                answer_line = None
                for line in reversed(lines):
                    if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('print'):
                        try:
                            # Try to parse as number
                            if '.' in line:
                                final_answer = float(line.strip())
                            else:
                                final_answer = int(line.strip())
                            answer_line = line.strip()
                            break
                        except:
                            continue
                
                if final_answer is None:
                    raise ValueError("Could not extract numerical answer from code output")
                
                # Step 6: Validate answer makes sense in context
                validation = await self.generate(
                    instruction=f"""Validate the computed answer for this Bengali math problem.
                    Computed answer: {final_answer}
                    Problem context: {self.problem_text}
                    Mathematical model: {model_spec}
                    
                    Check:
                    1. Does the answer satisfy all problem constraints?
                    2. Is the magnitude reasonable? (e.g., not negative when impossible, not extremely large)
                    3. Does it match the expected unit context?
                    4. Are there any logical inconsistencies?
                    
                    Respond with "VALID" if answer is correct, or "INVALID: [reason]" if not.""",
                    context=code_result
                )
                
                if "VALID" in validation.upper() and "INVALID" not in validation.upper():
                    break  # Success!
                else:
                    last_error = f"Validation failed: {validation}"
                    # Revise model spec based on validation feedback
                    model_spec = await self.revise(
                        instruction=f"""Revise the mathematical model specification based on validation feedback.
                        Validation feedback: {validation}
                        Previous model: {model_spec}
                        
                        Focus on:
                        - Correcting any misinterpretations of the problem
                        - Fixing mathematical relationships
                        - Adjusting constraints or units
                        - Clarifying ambiguous aspects
                        
                        Output revised model specification.""",
                        context=model_spec
                    )
                    
            except Exception as e:
                last_error = str(e)
                # Revise model spec based on error
                model_spec = await self.revise(
                    instruction=f"""Revise the mathematical model specification based on execution error.
                    Error: {str(e)}
                    Previous model: {model_spec}
                    
                    Focus on:
                    - Fixing mathematical formulation
                    - Correcting unit handling
                    - Adjusting constraints
                    - Simplifying complex expressions
                    
                    Output revised model specification.""",
                    context=model_spec
                )
        
        # Step 7: Final ensemble with explanation (for robustness)
        if final_answer is None:
            # Fallback: try to extract answer from last code result
            final_answer = 0  # Default fallback
            
        explanation = await self.generate(
            instruction=f"""Generate a step-by-step explanation in English for how the answer {final_answer} was derived from the Bengali problem.
            Include:
            - Initial problem interpretation
            - Key mathematical steps
            - Unit handling
            - Constraint satisfaction
            - Final verification
            
            This explanation will be used for final validation.""",
            context=f"Problem: {self.problem_text}\nModel: {model_spec}\nAnswer: {final_answer}"
        )
        
        # Final validation with explanation
        final_validation = await self.generate(
            instruction=f"""Final validation: Does the explanation logically lead to the answer {final_answer} for the given Bengali problem?
            Problem: {self.problem_text}
            Explanation: {explanation}
            Answer: {final_answer}
            
            Respond with "CONFIRMED" if everything is correct, or "REJECTED: [reason]" if not.""",
            context=explanation
        )
        
        if "REJECTED" in final_validation.upper():
            # One last attempt with deep analysis
            deep_analysis = await self.generate(
                instruction=f"""Perform deep analysis of this Bengali math problem.
                Problem: {self.problem_text}
                Previous answer: {final_answer}
                Previous explanation: {explanation}
                Rejection reason: {final_validation}
                
                Start from scratch:
                1. Re-interpret the Bengali text carefully
                2. Identify any missed nuances or misinterpretations
                3. Build correct mathematical model
                4. Compute answer step by step
                5. Verify against all constraints
                
                Output only the final numerical answer.""",
                context=""
            )
            
            try:
                # Try to parse the deep analysis result as a number
                lines = deep_analysis.split('\n')
                for line in reversed(lines):
                    if line.strip():
                        try:
                            if '.' in line:
                                final_answer = float(line.strip())
                            else:
                                final_answer = int(line.strip())
                            break
                        except:
                            continue
            except:
                pass  # Keep previous answer if deep analysis fails
        
        return str(final_answer)