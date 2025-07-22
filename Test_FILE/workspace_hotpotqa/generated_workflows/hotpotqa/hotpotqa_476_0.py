# Workflow ID: hotpotqa_476_0
# Benchmark: hotpotqa
# Data Indices: [2237, 3338, 483, 1815]

<operator id="1">
        <instruction>Identify the common occupation between Henry King and Clarence G. Badger by analyzing their professional roles in film.</instruction>
        <input>context</input>
        <output>occupation</output>
    </operator>
    <operator id="2">
        <instruction>Verify that both individuals were involved in directing films during their careers.</instruction>
        <input>occupation</input>
        <output>verification</output>
    </operator>
    <operator id="3">
        <instruction>Confirm that the occupation identified is consistent across both biographical entries in the context.</instruction>
        <input>verification</input>
        <output>final_answer</output>
    </operator>