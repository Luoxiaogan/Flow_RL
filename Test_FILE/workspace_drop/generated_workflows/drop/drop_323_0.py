# Workflow ID: drop_323_0
# Benchmark: drop
# Data Indices: [1428, 2445, 1076, 3911]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key information in the passage related to field goals and their distances. Focus on finding the second longest field goal mentioned.</instruction>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <instruction>Extract all field goal distances from the passage and sort them in descending order to determine the second longest.</instruction>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <instruction>From the sorted list of field goal distances, identify the second longest distance and find which player kicked it.</instruction>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="output">
        <data>4</data>
    </node>