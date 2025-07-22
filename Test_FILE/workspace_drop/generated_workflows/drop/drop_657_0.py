# Workflow ID: drop_657_0
# Benchmark: drop
# Data Indices: [3480, 1229, 238, 874, 754]

<agent id="1" type="extract">
        <instruction>Extract all numerical values related to the question from the passage. Focus only on the relevant data points.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter out irrelevant numerical values and keep only those directly answering the question.</instruction>
    </agent>
    <agent id="3" type="compute">
        <instruction>Perform any necessary calculation (e.g., subtraction, percentage, comparison) based on filtered values.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Check if the computed result matches the logical context of the question. Ensure units and logic are correct.</instruction>
    </agent>
    <agent id="5" type="finalize">
        <instruction>Return the final answer in a concise format that directly answers the question.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>