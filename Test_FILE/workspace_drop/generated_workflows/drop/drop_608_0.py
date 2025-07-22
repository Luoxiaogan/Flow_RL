# Workflow ID: drop_608_0
# Benchmark: drop
# Data Indices: [2442, 664, 3468, 917, 2549]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract the relevant numerical data from the passage related to the question. Identify the total completed passes and incomplete passes for Billy Kilmer.</instruction>
        <output>completed_passes = 120, incomplete_passes = 105</output>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the difference between completed passes and incomplete passes by subtracting incomplete passes from completed passes.</instruction>
        <output>difference = completed_passes - incomplete_passes</output>
    </node>
    <node id="4" type="output">
        <param name="result">difference</param>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>