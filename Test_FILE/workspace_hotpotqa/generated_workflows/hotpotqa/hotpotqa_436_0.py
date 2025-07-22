# Workflow ID: hotpotqa_436_0
# Benchmark: hotpotqa
# Data Indices: [3325, 2389, 2585, 1329, 3841]

<operator id="1">
        <instruction>Identify the key entities in the problem and extract their birth dates.</instruction>
        <input>problem</input>
        <output>entity_birth_dates</output>
    </operator>
    
    <operator id="2">
        <instruction>Compare the birth dates to determine who is older between the two tennis players.</instruction>
        <input>entity_birth_dates</input>
        <output>older_player</output>
    </operator>
    
    <operator id="3">
        <instruction>Format the final answer to clearly state which player is older.</instruction>
        <input>older_player</input>
        <output>final_answer</output>
    </operator>