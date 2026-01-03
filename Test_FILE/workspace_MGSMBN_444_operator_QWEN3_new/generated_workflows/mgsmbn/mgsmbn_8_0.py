# Workflow ID: mgsmbn_8_0
# Benchmark: mgsmbn
# Data Indices: [89, 77]

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

    async def run_workflow(self):
        """
        Universal workflow for MGSM Bengali math word problems.
        Architecture: Semantic Parsing → Parallel Strategy Generation → Validation & Synthesis
        """
        import asyncio
        import re

        # PHASE 1: SEMANTIC PARSING & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem to extract:
1. All numerical values and their contextual meaning (e.g., "30 cars" = initial count)
2. Named entities (teachers, cars, whiteboards, etc.) and their roles
3. Actions and events with temporal/causal relationships (e.g., "first 15 minutes", "then", "after that")
4. Explicit and implicit constraints (e.g., "can't have negative cars", "whole teachers only")
5. The unknown being asked for (e.g., "how many cars passed first?")
6. Problem archetype classification: Sequential, Rate, Proportional, Distribution, Comparison, or Multi-entity

Structure your output as:
Entities: [list with descriptions]
Actions: [chronological list with dependencies]
Constraints: [list of hard and soft constraints]
Unknown: [clear statement of what to solve for]
Classification: [one primary archetype]

Be meticulous. Every number and verb matters.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        # Three complementary approaches: Direct Equation, Step Simulation, Unit Analysis
        strategy_instructions = [
            """You are a mathematical modeler. Translate the problem narrative directly into algebraic equations.
- Identify variables for unknowns
- Express relationships as equations using extracted numbers and constraints
- Solve step by step, showing all arithmetic
- Verify solution satisfies all constraints
Output only the final numerical answer and the key equation used.""",
            
            """You are a scenario simulator. Re-enact the problem step by step as if directing a play.
- Start with initial state (e.g., "30 cars waiting")
- For each action/event: state what happens, update counts/variables, note new state
- Track units and totals at each step
- If you reach a contradiction, backtrack and reinterpret the narrative
- End with the answer to the unknown
Output the step-by-step simulation and final answer.""",
            
            """You are a unit analysis expert. Solve using dimensional analysis and proportional reasoning.
- Identify all units (cars, minutes, wipes, etc.) and their relationships
- Set up ratios, proportions, or unit conversions as needed
- Cancel units systematically to arrive at the desired unknown
- Cross-check with constraints
Output the unit-based reasoning and final answer."""
        ]

        # Generate three parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) 
              for instr in strategy_instructions]
        )

        # PHASE 3: ENSEMBLE SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction="""You are a master math teacher evaluating three student solutions.
Compare these three attempts:
1. Direct Equation approach
2. Step-by-Step Simulation
3. Unit Analysis

Grade each on:
- Correct final numerical answer (1 point)
- Logical step-by-step reasoning (1 point)
- Unit consistency and constraint adherence (1 point)
- Temporal/causal order respect (1 point)

Select the solution with the highest score. If tie, prefer the one with clearest alignment to the original narrative.
If all solutions agree on the answer, return that answer with "Consensus: " prefix.
If they conflict, return the highest-scoring solution's answer with "Selected: " prefix.

Output ONLY the final numerical answer as a single number (integer or decimal).""",
            contexts_list=solution_attempts
        )

        # PHASE 4: VALIDATION LOOP (up to 2 iterations)
        final_answer = synthesized_solution
        for validation_round in range(2):
            validation = await self.revise(
                instruction=f"""Critically validate this answer against the original problem:
Answer: {final_answer}

Check:
1. Does this answer make sense in context? (e.g., no negative cars, fractional teachers)
2. Does it satisfy all explicit and implicit constraints from the analysis?
3. Is the temporal/causal order respected?
4. Are units consistent throughout?
5. Does it directly answer the unknown identified?

If any issue is found, explain the error and provide the corrected answer.
If no issues, output "VALID: {final_answer}".

Be brutally honest. If wrong, fix it.""",
                context=problem_analysis
            )

            # Check if validation found an error
            if "VALID:" in validation:
                final_answer = validation.split("VALID:")[-1].strip()
                break
            else:
                # Extract corrected answer from validation
                # Look for a number in the validation response
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', validation)
                if numbers:
                    final_answer = numbers[0]  # Take first number as corrected answer
                # Continue to next validation round if needed

        return final_answer