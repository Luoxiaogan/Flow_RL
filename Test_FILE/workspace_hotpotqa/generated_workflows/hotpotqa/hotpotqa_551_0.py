# Workflow ID: hotpotqa_551_0
# Benchmark: hotpotqa
# Data Indices: [3048, 3677, 1304, 356]

<agent id="1" type="reasoning">
        <instruction>Identify the key relationships and lineage in the context to trace the great-great-great-grandson of John Lok.</instruction>
        <input>problem</input>
        <output>traced_lineage</output>
    </agent>
    <agent id="2" type="filter">
        <instruction>From the traced lineage, extract only the direct descendants leading to the great-great-great-grandson.</instruction>
        <input>traced_lineage</input>
        <output>direct_descendants</output>
    </agent>
    <agent id="3" type="lookup">
        <instruction>Match the direct descendants with known individuals in the provided context who are explicitly identified as great-great-great-grandsons.</instruction>
        <input>direct_descendants</input>
        <output>potential_match</output>
    </agent>
    <agent id="4" type="validate">
        <instruction>Verify that the potential match is indeed the correct great-great-great-grandson by confirming generational steps and names.</instruction>
        <input>potential_match</input>
        <output>validated_result</output>
    </agent>
    <agent id="5" type="combine">
        <instruction>Combine all validated information into a single coherent answer.</instruction>
        <input>validated_result</input>
        <output>final_answer</output>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>