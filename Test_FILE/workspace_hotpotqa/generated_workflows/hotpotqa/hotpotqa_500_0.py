# Workflow ID: hotpotqa_500_0
# Benchmark: hotpotqa
# Data Indices: [405, 2415, 1511, 2312]

<operator id="0" type="agent">
        <instruction>Think step by step to identify the key information needed to solve the problem.</instruction>
        <input>problem</input>
        <output>step_by_step_analysis</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>Extract relevant entities and dates from the context that relate to the question.</instruction>
        <input>step_by_step_analysis</input>
        <output>extracted_entities</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Determine which entity in the extracted data answers the core question directly.</instruction>
        <input>extracted_entities</input>
        <output>candidate_answer</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify the candidate answer against all available context to ensure accuracy.</instruction>
        <input>candidate_answer</input>
        <output>verified_answer</output>
    </operator>
    <operator id="4" type="agent">
        <instruction>Ensure the final output is concise, clear, and directly addresses the original question.</instruction>
        <input>verified_answer</input>
        <output>final_answer</output>
    </operator>
    <operator id="5" type="agent">
        <instruction>Check for any logical inconsistencies or missing steps in the reasoning chain.</instruction>
        <input>final_answer</input>
        <output>quality_check</output>
    </operator>
    <operator id="6" type="agent">
        <instruction>Return the final verified answer as the solution.</instruction>
        <input>quality_check</input>
        <output>solution</output>
    </operator>