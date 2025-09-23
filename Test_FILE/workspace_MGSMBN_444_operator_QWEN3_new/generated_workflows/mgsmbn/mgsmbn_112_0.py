# Workflow ID: mgsmbn_112_0
# Benchmark: mgsmbn
# Data Indices: [161]

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

        # PHASE 1: PARALLEL DECOMPOSITION
        # Extract problem structure from multiple angles simultaneously
        decomposition_tasks = [
            self.generate(
                instruction="""Perform deep semantic decomposition of the Bengali math problem. Ignore script specifics; focus on abstract quantitative relationships. Extract:
                1. All named entities (people, objects) and their roles
                2. All numerical values with their semantic meaning (not just raw numbers)
                3. Temporal sequences and dependencies (what happens when)
                4. Mathematical relationships (ratios, percentages, operations implied)
                5. Units and their conversions if needed
                6. The explicit question being asked
                7. Any constraints or boundary conditions (e.g., "whole numbers only")
                Output as a structured JSON-like block with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Identify the core mathematical archetype of this problem. Classify it into one or more of:
                - Sequential operations (step-by-step changes)
                - Rate problems (speed, work, unit price)
                - Proportional reasoning (ratios, percentages, scaling)
                - Distribution (sharing, division, remainders)
                - Comparison (differences, "how many more")
                - Multi-entity tracking (multiple actors with different values)
                Also identify:
                - Required operations (add, subtract, multiply, divide, percentage, etc.)
                - Hidden steps (calculations not explicitly stated but necessary)
                - Potential pitfalls (common misinterpretations)
                Format as a classification report with confidence scores for each category.""",
                context=""
            ),
            self.generate(
                instruction="""Generate a "naive solution" — the most straightforward, surface-level interpretation of the problem. This will likely contain errors or oversimplifications, but serves as a baseline. Include:
                - Direct extraction of numbers and operations
                - Assumed sequence of calculations
                - Preliminary answer (even if likely wrong)
                This helps us identify where deeper analysis is needed.""",
                context=""
            )
        ]
        
        decomposition_results = await asyncio.gather(*decomposition_tasks)
        structured_analysis, problem_classification, naive_solution = decomposition_results

        # Build cumulative context for next phase
        decomposition_context = f"""STRUCTURED ANALYSIS:
{structured_analysis}

PROBLEM CLASSIFICATION:
{problem_classification}

NAIVE SOLUTION (for contrast):
{naive_solution}"""

        # PHASE 2: STRATEGY ENSEMBLE
        # Generate multiple solution approaches in parallel
        strategy_instructions = [
            """Develop a CHRONOLOGICAL SIMULATION approach:
            - Model the problem as a sequence of events over time
            - Calculate state changes step by step (week by week, person by person)
            - Track running totals and intermediate values
            - Especially useful for problems with temporal dependencies or changing rates
            Show all intermediate steps explicitly.""",
            
            """Develop an ALGEBRAIC AGGREGATION approach:
            - Derive a single mathematical formula that captures the entire problem
            - Use variables for unknowns, solve symbolically where possible
            - Combine terms, factor expressions, simplify before plugging in numbers
            - Especially useful for proportional reasoning or percentage problems
            Show the derivation of the formula before calculation.""",
            
            """Develop a UNIT-RATE SCALING approach:
            - Identify base units (per week, per item, per person)
            - Calculate effective rates after all modifiers (raises, discounts, etc.)
            - Scale to required total (multiply by time, quantity, etc.)
            - Add fixed amounts or bonuses at the end
            - Especially useful for salary, pricing, or work rate problems
            Show the unit rate derivation clearly."""
        ]

        strategy_tasks = [
            self.generate(
                instruction=f"""{strategy_instructions[0]}

Use this context from problem decomposition:
{decomposition_context}""",
                context=decomposition_context
            ),
            self.generate(
                instruction=f"""{strategy_instructions[1]}

Use this context from problem decomposition:
{decomposition_context}""",
                context=decomposition_context
            ),
            self.generate(
                instruction=f"""{strategy_instructions[2]}

Use this context from problem decomposition:
{decomposition_context}""",
                context=decomposition_context
            )
        ]

        candidate_solutions = await asyncio.gather(*strategy_tasks)

        # Select best approach via ensemble
        selected_solution = await self.ensemble(
            instruction="""Select the most appropriate solution approach based on:
            1. Alignment with problem structure (does it match the chronological/proportional/etc. nature?)
            2. Computational simplicity (fewer steps = less error-prone)
            3. Transparency (clear, auditable steps)
            4. Handling of edge cases (units, constraints, boundary conditions)
            5. Consistency with problem decomposition analysis
            Provide brief justification for selection, then output the chosen solution verbatim.""",
            contexts_list=candidate_solutions
        )

        # PHASE 3: ITERATIVE SELF-CRITIQUE & REFINEMENT
        current_solution = selected_solution
        max_iterations = 3
        
        for iteration in range(max_iterations):
            # Generate critique
            critique = await self.generate(
                instruction=f"""Critically evaluate this solution for:
                - Mathematical accuracy (check arithmetic, order of operations)
                - Unit consistency (are units preserved and converted correctly?)
                - Step validity (does each step follow logically from previous?)
                - Contextual plausibility (does answer make sense in real-world context?)
                - Completeness (are all problem elements addressed?)
                - Hidden step coverage (are implied calculations included?)
                If no errors found, respond with "VALID: [confidence score]". 
                If errors found, describe them specifically and suggest corrections.""",
                context=current_solution
            )

            # Check if critique found no errors
            if "VALID:" in critique.upper() and "ERROR" not in critique.upper():
                break
            
            # Revise solution based on critique
            current_solution = await self.revise(
                instruction=f"""Revise the solution to address the specific errors and suggestions in this critique:
                {critique}
                
                Maintain all correct parts, but fix identified issues.
                Add explicit justifications for corrected steps.
                Ensure final answer is clearly stated at the end.""",
                context=current_solution
            )

        # PHASE 4: FINAL VALIDATION & ANSWER EXTRACTION
        # Generate justification and final answer
        final_output = await self.generate(
            instruction="""Extract the final numerical answer from the solution and format it as a single number (integer or decimal). Also generate a one-sentence justification that shows the key calculation. Format exactly as:
            ANSWER: [number]
            JUSTIFICATION: [one sentence showing key calculation]

            Example:
            ANSWER: 114200
            JUSTIFICATION: 5000 + 52 * (2000 * 1.05) = 5000 + 109200 = 114200""",
            context=current_solution
        )

        # Extract just the number using regex (since output format is controlled)
        match = re.search(r'ANSWER:\s*([0-9,]+\.?[0-9]*)', final_output)
        if match:
            answer_str = match.group(1).replace(',', '')  # Remove commas
            try:
                # Convert to int if possible, otherwise float
                if '.' in answer_str:
                    final_answer = float(answer_str)
                else:
                    final_answer = int(answer_str)
            except ValueError:
                final_answer = float(answer_str) if '.' in answer_str else int(float(answer_str))
        else:
            # Fallback: try to extract any number from the solution
            number_match = re.search(r'([0-9,]+\.?[0-9]*)', current_solution)
            if number_match:
                answer_str = number_match.group(1).replace(',', '')
                final_answer = float(answer_str) if '.' in answer_str else int(answer_str)
            else:
                final_answer = 0  # Ultimate fallback

        return final_answer