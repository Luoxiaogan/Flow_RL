# Workflow ID: hotpotqa_164_0
# Benchmark: hotpotqa
# Data Indices: [3872, 2861, 300, 2844]

<operator id="0">
        <instruction>Identify the birth year of Ferenc Molnár from the context.</instruction>
        <input>context</input>
        <output>ferenc_birth_year</output>
    </operator>
    <operator id="1">
        <instruction>Identify the birth year of Karen Joy Fowler from the context.</instruction>
        <input>context</input>
        <output>karen_birth_year</output>
    </operator>
    <operator id="2">
        <instruction>Compare the birth years to determine who was born earlier.</instruction>
        <input>ferenc_birth_year, karen_birth_year</input>
        <output>earlier_born</output>
    </operator>
    <operator id="3">
        <instruction>Return the name of the writer born earlier.</instruction>
        <input>earlier_born</input>
        <output>final_answer</output>
    </operator>