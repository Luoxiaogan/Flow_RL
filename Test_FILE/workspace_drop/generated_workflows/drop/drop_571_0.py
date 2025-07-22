# Workflow ID: drop_571_0
# Benchmark: drop
# Data Indices: [1065, 521, 1053, 1517, 2404]

<node id="1" type="input">
        <prompt>Understand the problem and extract key temporal information.</prompt>
    </node>
    
    <node id="2" type="operator">
        <prompt>Identify the start and end dates of each phase of the conflict.</prompt>
        <dependencies>1</dependencies>
    </node>
    
    <node id="3" type="operator">
        <prompt>Calculate the duration of the first phase in months.</prompt>
        <dependencies>2</dependencies>
    </node>
    
    <node id="4" type="operator">
        <prompt>Calculate the duration of the resumption phase in months.</prompt>
        <dependencies>2</dependencies>
    </node>
    
    <node id="5" type="operator">
        <prompt>Add both durations to get total months.</prompt>
        <dependencies>3,4</dependencies>
    </node>
    
    <node id="6" type="output">
        <prompt>Return the total number of months the war lasted.</prompt>
        <dependencies>5</dependencies>
    </node>