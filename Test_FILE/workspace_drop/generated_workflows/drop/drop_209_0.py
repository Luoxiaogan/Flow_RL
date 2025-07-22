# Workflow ID: drop_209_0
# Benchmark: drop
# Data Indices: [2265, 2179, 3710, 2184]

<node id="1" type="input">
        <description>Receive the problem input</description>
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the key elements in the passage relevant to the question. Focus on numerical values and player actions mentioned.</instruction>
        <depends_on>1</depends_on>
    </node>
    
    <node id="3" type="agent">
        <instruction>Extract all field goal distances or yardage from the passage, focusing only on those that directly relate to the question asked.</instruction>
        <depends_on>2</depends_on>
    </node>
    
    <node id="4" type="agent">
        <instruction>Determine which field goals are relevant based on the specific question (e.g., total yards for one player, longest of the game).</instruction>
        <depends_on>3</depends_on>
    </node>
    
    <node id="5" type="agent">
        <instruction>Perform necessary calculations: summing up total yards or identifying the maximum value among extracted numbers.</instruction>
        <depends_on>4</depends_on>
    </node>
    
    <node id="6" type="output">
        <description>Return the final answer based on the computed result from the previous step.</description>
        <depends_on>5</depends_on>
    </node>