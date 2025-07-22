# Workflow ID: drop_786_0
# Benchmark: drop
# Data Indices: [3408, 1056, 144, 2768]

<node id="1" type="input">
        <prompt>Extract all scoring plays from the passage and identify which ones occurred in the first half.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify each scoring play and its corresponding quarter. Focus only on the first half (first and second quarters).</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>For each first-half scoring play, determine the number of points scored (touchdown = 6, field goal = 3, extra point = 1, two-point conversion = 2).</prompt>
    </node>
    <node id="4" type="operator">
        <prompt>Sum the total points from all first-half scoring plays.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the total number of points scored in the first half.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>