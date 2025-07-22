# Workflow ID: hotpotqa_349_0
# Benchmark: hotpotqa
# Data Indices: [2097, 1555, 347, 3773, 2335]

<operator id="0" type="agent">
        <instruction>Think step by step. Identify the key elements in the question: the actor, the genre of the film, and the director.</instruction>
        <input>problem</input>
        <output>step1</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>Based on the context, find the film where Taron Egerton starred that is a biographical sports comedy-drama directed by Dexter Fletcher.</instruction>
        <input>step1</input>
        <output>step2</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Extract the release year of the film identified in step 2.</instruction>
        <input>step2</input>
        <output>year</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify that the extracted year matches the correct film from the context.</instruction>
        <input>year</input>
        <output>verification</output>
    </operator>
    <operator id="4" type="agent">
        <instruction>Return the verified year as the final answer.</instruction>
        <input>verification</input>
        <output>final_answer</output>
    </operator>
    <connection from="0" to="1"/>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>