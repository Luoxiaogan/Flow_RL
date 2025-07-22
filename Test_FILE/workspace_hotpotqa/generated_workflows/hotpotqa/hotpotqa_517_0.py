# Workflow ID: hotpotqa_517_0
# Benchmark: hotpotqa
# Data Indices: [2774, 2896, 1443, 3420, 2775]

<operator id="1" type="agent">
        <instruction>Identify the key elements in the question and locate the relevant context.</instruction>
        <input>problem</input>
        <output>key_elements, relevant_context</output>
    </operator>

    <operator id="2" type="agent">
        <instruction>Extract the specific answer from the relevant context based on the key elements.</instruction>
        <input>key_elements, relevant_context</input>
        <output>potential_answer</output>
    </operator>

    <operator id="3" type="agent">
        <instruction>Validate the potential answer against all known facts in the context to ensure accuracy.</instruction>
        <input>potential_answer, relevant_context</input>
        <output>validated_answer</output>
    </operator>

    <operator id="4" type="agent">
        <instruction>Check for any conflicting or ambiguous information that might affect the final answer.</instruction>
        <input>relevant_context</input>
        <output>conflict_check</output>
    </operator>

    <operator id="5" type="agent">
        <instruction>Combine the validated answer with the conflict check result to produce a definitive output.</instruction>
        <input>validated_answer, conflict_check</input>
        <output>final_answer</output>
    </operator>

    <operator id="6" type="agent">
        <instruction>Ensure the final answer matches the format required by the question (e.g., name, date, title).</instruction>
        <input>final_answer</input>
        <output>formatted_answer</output>
    </operator>

    <operator id="7" type="agent">
        <instruction>Review the entire workflow for logical consistency and completeness.</instruction>
        <input>formatted_answer</input>
        <output>quality_assurance</output>
    </operator>

    <operator id="8" type="agent">
        <instruction>Return the final, verified answer as the output of the graph.</instruction>
        <input>quality_assurance</input>
        <output>answer</output>
    </operator>