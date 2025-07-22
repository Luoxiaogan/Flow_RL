# Workflow ID: hotpotqa_523_0
# Benchmark: hotpotqa
# Data Indices: [236, 2378, 1790, 2874, 1381]

<agent id="1">
        <instruction>Identify the key entities and relationships in the problem statement.</instruction>
        <output>Extract relevant entities and their connections.</output>
    </agent>
    <agent id="2">
        <instruction>Map the extracted entities to potential solutions based on known facts or logical deductions.</instruction>
        <output>Generate candidate solutions with supporting evidence.</output>
    </agent>
    <agent id="3">
        <instruction>Evaluate each candidate solution for consistency with all provided context and constraints.</instruction>
        <output>Rank candidates by confidence level.</output>
    </agent>
    <agent id="4">
        <instruction>Select the highest-confidence candidate as the final answer.</instruction>
        <output>Return the correct answer.</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>