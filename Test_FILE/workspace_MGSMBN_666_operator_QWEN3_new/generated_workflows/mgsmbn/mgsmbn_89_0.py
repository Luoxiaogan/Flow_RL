# Workflow ID: mgsmbn_89_0
# Benchmark: mgsmbn
# Data Indices: [127, 96]

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

        # Step 1: Classify problem complexity to determine processing depth
        classification = await self.generate(
            instruction="""Analyze this Bengali math word problem and classify its complexity:
            - SIMPLE: Single operation, one entity, no hidden steps (e.g., multiplication of known quantities)
            - MODERATE: Multiple operations or entities, clear relationships
            - COMPLEX: Ambiguous phrasing, hidden steps, unit conversions, or comparative reasoning
            
            Also identify:
            - Main question being asked
            - Key numerical values and their meanings
            - Units involved
            - Potential pitfalls or ambiguities
            
            Return classification in format: "CLASSIFICATION: [SIMPLE/MODERATE/COMPLEX]" followed by analysis.""",
            context=""
        )

        # Step 2: Conditional branching based on complexity
        if "SIMPLE" in classification:
            # Direct decomposition for simple problems
            decomposition = await self.decompose(
                instruction="""Break this simple problem into minimal necessary steps:
                - Identify the single mathematical operation needed
                - Extract the two key numbers involved
                - Define the calculation to perform
                - Specify the expected output format
                Return as structured subproblems with dependencies.""",
                context=""
            )
        else:
            # For moderate/complex: Generate multiple interpretations in parallel
            interpretation_tasks = [
                self.generate(
                    instruction="""Interpret this problem with focus on LITERAL TRANSLATION:
                    - Translate Bengali phrases to mathematical relationships word-for-word
                    - Identify all numbers and their direct associations
                    - Map verbs to operations (e.g., 'দৌড়ান' → distance calculation)
                    - Preserve original units and quantities exactly as stated""",
                    context=""
                ),
                self.generate(
                    instruction="""Interpret this problem with focus on MATHEMATICAL MODELING:
                    - Ignore literal phrasing, focus on underlying mathematical structure
                    - Identify what is being asked and what operations are needed
                    - Convert real-world actions to mathematical expressions
                    - Handle implicit steps (e.g., round trips = 2 × distance)""",
                    context=""
                ),
                self.generate(
                    instruction="""Interpret this problem with focus on UNIT & CONTEXT TRACKING:
                    - Track all units throughout the problem
                    - Identify potential unit conversions needed
                    - Flag any context constraints (e.g., can't have negative people)
                    - Ensure final answer format matches question requirements""",
                    context=""
                )
            ]
            
            interpretations = await asyncio.gather(*interpretation_tasks)
            
            # Ensemble to reconcile interpretations
            reconciled = await self.ensemble(
                instruction="""Synthesize these three interpretations into one coherent problem understanding:
                - Resolve contradictions by choosing most mathematically sound interpretation
                - Preserve all key numbers and their correct meanings
                - Clarify any ambiguous relationships
                - Ensure units and context constraints are properly handled
                - Output should be a clear, unambiguous problem restatement ready for decomposition""",
                contexts_list=interpretations
            )
            
            # Decompose based on reconciled understanding
            decomposition = await self.decompose(
                instruction="""Break this problem into atomic, sequentially dependent subproblems:
                - Each subproblem should be solvable with one mathematical operation
                - Define clear dependencies between subproblems
                - Include unit tracking in each step
                - Final subproblem should directly answer the main question
                Return as structured list with 'id', 'description', and 'dependencies'.""",
                context=reconciled
            )

        # Step 3: Solve each subproblem sequentially respecting dependencies
        subproblem_results = {}
        
        # Sort subproblems by dependencies (topological sort implied by dependency strings)
        # For simplicity, we'll process in order and assume dependencies are satisfied by earlier IDs
        for subproblem in decomposition:
            sub_id = subproblem['id']
            description = subproblem['description']
            
            # Generate precise mathematical formulation for this subproblem
            formulation = await self.generate(
                instruction=f"""Convert this subproblem into a precise mathematical expression or equation:
                Subproblem: {description}
                
                Requirements:
                - Use only numbers and standard mathematical operators (+, -, ×, ÷)
                - Include units in parentheses after each number if applicable
                - If this depends on previous results, reference them as [RESULT_ID]
                - Output ONLY the mathematical expression, nothing else""",
                context=""
            )
            
            # Execute the calculation
            calculation_result = await self.programmer(
                instruction=f"""Compute this mathematical expression:
                {formulation}
                
                Context from previous subproblems: {str(subproblem_results)}
                
                Requirements:
                - Show all steps if multi-step
                - Maintain precision throughout
                - Return final numerical result with units if applicable""",
                context=formulation
            )
            
            # Validate result makes sense in context
            validation = await self.generate(
                instruction=f"""Validate this result in context of the original problem:
                Subproblem: {description}
                Result: {calculation_result}
                Previous results: {str(subproblem_results)}
                
                Check for:
                - Negative quantities where impossible (people, items, etc.)
                - Fractional results where integers are required
                - Unit mismatches
                - Results that contradict problem constraints
                
                If valid, return "VALID". If invalid, explain why and suggest correction.""",
                context=calculation_result
            )
            
            # If invalid, attempt revision (simple case - in practice might need more complex handling)
            if "VALID" not in validation:
                calculation_result = await self.revise(
                    instruction=f"""Correct this calculation based on validation feedback:
                    Original: {calculation_result}
                    Feedback: {validation}
                    Subproblem: {description}
                    Previous results: {str(subproblem_results)}""",
                    context=calculation_result
                )
            
            subproblem_results[sub_id] = calculation_result

        # Step 4: Extract final answer from last subproblem result
        final_subproblem_id = decomposition[-1]['id']
        final_result = subproblem_results[final_subproblem_id]
        
        # Summarize to extract pure numerical answer
        numerical_answer = await self.summarize(
            instruction="""Extract ONLY the numerical answer from the following text:
            - If multiple numbers exist, select the one that directly answers the original question
            - Remove all units, text, and explanations
            - Return ONLY the number (integer or decimal)
            - If answer is fractional, convert to decimal
            - Do not add any formatting or text""",
            context=final_result
        )
        
        # Final validation: ensure it's a clean number
        # Clean any remaining text using regex
        match = re.search(r'[-+]?\d*\.\d+|\d+', numerical_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (shouldn't happen in well-formed problems)
            return numerical_answer.strip()