# Workflow ID: drop_494_0
# Benchmark: drop
# Data Indices: [2312, 1218, 1549, 1270]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the passage related to the question. Focus on players, scores, and actions mentioned.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Determine if any player scored more than one touchdown based on the extracted data.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the count of touchdowns per player to confirm who scored multiple times.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the name of the player who scored more than one touchdown.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>