# Workflow ID: hotpotqa_28_0
# Benchmark: hotpotqa
# Data Indices: [1860, 3621, 2486, 1885, 689]

<agent id="1" type="reasoning">
        <instruction>Think step by step to determine the connection between the singer of "I've Got Love on My Mind" and Nat King Cole.</instruction>
        <input>problem</input>
        <output>connection</output>
    </agent>
    <agent id="2" type="lookup">
        <instruction>Find the relationship between Natalie Cole and Nat King Cole using contextual data.</instruction>
        <input>problem</input>
        <output>relationship</output>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify that Natalie Cole is indeed the singer of "I've Got Love on My Mind" and confirm her relation to Nat King Cole.</instruction>
        <input>problem</input>
        <output>verification_result</output>
    </agent>
    <agent id="4" type="synthesis">
        <instruction>Combine the outputs from agents 1, 2, and 3 to produce a final answer.</instruction>
        <input>connection, relationship, verification_result</input>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="4"/>
    <edge from="2" to="4"/>
    <edge from="3" to="4"/>