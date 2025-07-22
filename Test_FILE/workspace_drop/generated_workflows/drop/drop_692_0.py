# Workflow ID: drop_692_0
# Benchmark: drop
# Data Indices: [3567, 841, 3513, 759, 794]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify all relevant numerical data points related to the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Extract and list all values that match the criteria in the question. For example, if the question asks about field goals between 20 and 30 yards, filter for those exact yardages.</prompt>
    </node>
    <node id="3" type="filter">
        <prompt>From the extracted values, isolate only those that satisfy the condition specified in the question (e.g., field goals between 20–30 yards).</prompt>
    </node>
    <node id="4" type="count">
        <prompt>Count how many items remain after filtering — this is your answer.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final count as the solution to the question.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>