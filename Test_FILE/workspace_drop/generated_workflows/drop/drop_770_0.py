# Workflow ID: drop_770_0
# Benchmark: drop
# Data Indices: [650, 2959, 1493, 3570]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the passage to identify all field goal distances mentioned for the relevant kicker.
        </instruction>
        <input>problem</input>
        <output>field_goals</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            From the list of field goals, determine the longest and shortest values.
        </instruction>
        <input>field_goals</input>
        <output>longest, shortest</output>
    </node>
    
    <node id="4" type="operator">
        <operation>longest - shortest</operation>
        <input>longest, shortest</input>
        <output>difference</output>
    </node>
    
    <node id="5" type="output">
        <param name="result" type="int"/>
        <input>difference</input>
    </node>