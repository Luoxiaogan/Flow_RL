# Workflow ID: hotpotqa_353_0
# Benchmark: hotpotqa
# Data Indices: [808, 1552, 3257, 2985, 2529]

<node id="1" type="input">
        <prompt>Understand the problem and identify key entities.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Extract relevant information from context: Identify the regional airline brand name used by Delta Air Lines that includes Atlantic Southeast Airlines and Endeavor Air.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify if the extracted brand name matches the definition of a regional airline brand under Delta Air Lines.</prompt>
    </node>
    
    <node id="4" type="agent">
        <prompt>Check if both Atlantic Southeast Airlines and Endeavor Air are part of this brand, based on historical and operational details.</prompt>
    </node>
    
    <node id="5" type="agent">
        <prompt>Confirm that no other brand (e.g., United Express, American Eagle) is associated with these carriers in the context provided.</prompt>
    </node>
    
    <node id="6" type="agent">
        <prompt>Combine all findings to determine the correct regional airline brand name for Delta Air Lines.</prompt>
    </node>
    
    <node id="7" type="output">
        <prompt>Return the final answer as a string representing the regional airline brand name.</prompt>
    </node>

    <!-- Edges -->
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>
    <edge from="6" to="7"/>