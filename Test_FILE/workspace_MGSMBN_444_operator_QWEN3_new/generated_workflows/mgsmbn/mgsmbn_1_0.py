# Workflow ID: mgsmbn_1_0
# Benchmark: mgsmbn
# Data Indices: [79, 27]

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

        # PHASE 1: PARALLEL EXTRACTION - Build problem structure
        entity_extraction, number_extraction, dependency_extraction = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities (people, objects) and their roles. 
                For each, list: name, role, associated actions, and any mentioned quantities. 
                Format as bullet points. Do NOT calculate or infer - only extract explicit mentions.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all numerical values, units, and mathematical relationships. 
                List each number with: value, unit (টাকা, বার, দিন, etc.), what it quantifies, and any comparative phrases (e.g., '1/4 গুণ বেশি'). 
                Format as numbered list. Do NOT perform calculations.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all dependencies and operation sequences. 
                Map which values depend on others, chronological order of events, and required calculation steps. 
                Use arrows (→) to show dependencies. Highlight any implicit constraints (e.g., must be integer, non-negative).""",
                context=""
            )
        )

        # Synthesize into unified problem structure
        problem_structure = await self.generate(
            instruction=f"""Synthesize the following extractions into a single coherent problem graph:
            Entities: {entity_extraction}
            Numbers: {number_extraction}
            Dependencies: {dependency_extraction}
            
            Create a step-by-step calculation plan that respects dependencies and constraints. 
            For each step: state what to calculate, from which values, and in what order. 
            Flag any potential ambiguities or missing information.""",
            context=f"{entity_extraction}\n\n{number_extraction}\n\n{dependency_extraction}"
        )

        # PHASE 2: PARALLEL SOLUTION GENERATION - Multiple strategies
        direct_calculation, algebraic_model, unit_scaling = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct arithmetic following the plan:
                {problem_structure}
                
                Show each calculation step explicitly with units. 
                Convert units to common base before operating. 
                Verify each intermediate result against constraints (non-negative, integer if required). 
                Box final answer.""",
                context=problem_structure
            ),
            self.generate(
                instruction=f"""Solve by setting up algebraic equations based on:
                {problem_structure}
                
                Define variables for unknowns. Write equations for each relationship. 
                Solve systematically. Track units throughout. 
                Verify solution satisfies all original conditions. Box final answer.""",
                context=problem_structure
            ),
            self.generate(
                instruction=f"""Solve using unit rate or scaling approach if applicable:
                {problem_structure}
                
                Find base unit rate (e.g., cost per item, rings per person). 
                Scale to required quantity. Show dimensional analysis. 
                Check for proportionality constraints. Box final answer.""",
                context=problem_structure
            )
        )

        # PHASE 3: VALIDATION & REFINEMENT
        validated_solutions = []
        for solution in [direct_calculation, algebraic_model, unit_scaling]:
            validated = await self.revise(
                instruction="""Critically validate this solution:
                1. Check unit consistency in every step
                2. Verify calculation order matches dependencies
                3. Ensure final answer respects implicit constraints (integer, non-negative, etc.)
                4. Confirm answer format matches problem requirements (number only)
                5. Fix any errors found
                
                If solution is invalid, return 'INVALID'. Otherwise, return corrected solution with final answer boxed.""",
                context=solution
            )
            validated_solutions.append(validated)

        # PHASE 4: ENSEMBLE DECISION - Synthesize best answer
        final_answer = await self.ensemble(
            instruction="""Select or synthesize the best final answer from these solutions:
            - Prefer solutions that explicitly track units and show step-by-step work
            - Require final answer to be a single number (integer or decimal) without units
            - Solutions marked 'INVALID' are disqualified
            - If multiple valid solutions agree, select that answer
            - If they disagree, synthesize by taking the most consistent steps across solutions
            - Final output must be ONLY the numerical answer (no text, no units)""",
            contexts_list=validated_solutions
        )

        # PHASE 5: SANITY CHECK LOOP (max 1 iteration)
        # Extract just the number from final answer
        number_match = re.search(r'[\d,]+\.?\d*', final_answer.replace(',', ''))
        if number_match:
            clean_answer = number_match.group(0)
            # Verify against problem constraints one last time
            sanity_check = await self.generate(
                instruction=f"""Final sanity check for answer {clean_answer}:
                Does this answer make sense given the problem context?
                - Is it within plausible range? (e.g., not billions for doorbell rings)
                - Does it satisfy all explicit and implicit constraints?
                - Is the magnitude reasonable compared to given numbers?
                
                If yes, return the number unchanged. If no, recalculate using most reliable method.""",
                context=f"Original answer: {final_answer}\n\nProblem structure: {problem_structure}"
            )
            # Extract number from sanity check
            final_match = re.search(r'[\d,]+\.?\d*', sanity_check.replace(',', ''))
            if final_match:
                return final_match.group(0)
        
        return final_answer.strip()