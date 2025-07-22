# Workflow ID: drop_200_0
# Benchmark: drop
# Data Indices: [479, 3149, 345, 2638]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract all touchdown values from the passage. Identify the longest and second longest touchdowns.</instruction>
        <param name="extract_touchdowns">True</param>
    </node>
    
    <node id="3" type="agent">
        <instruction>Calculate the difference between the longest and second longest touchdown distances.</instruction>
        <param name="calculate_difference">True</param>
    </node>
    
    <node id="4" type="output">
        <param name="result">The computed yard difference between the longest and second longest touchdowns.</param>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>