# Workflow ID: drop_54_0
# Benchmark: drop
# Data Indices: [1984, 781, 2616, 1752]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the passage to identify all instances where a kicker is mentioned and their associated field goals or scoring plays.
        </instruction>
        <input>problem</input>
        <output>kick_info</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            From the kick_info, extract only the field goals made by the kicker that were under 20 yards in distance.
        </instruction>
        <input>kick_info</input>
        <output>short_field_goals</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Count the number of short field goals identified in the previous step.
        </instruction>
        <input>short_field_goals</input>
        <output>count</output>
    </node>
    
    <node id="5" type="output">
        <input>count</input>
    </node>