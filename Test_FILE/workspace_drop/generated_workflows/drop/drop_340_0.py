# Workflow ID: drop_340_0
# Benchmark: drop
# Data Indices: [1013, 1217, 3618, 3145, 2725]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract numerical values from the passage relevant to the question. Identify key phrases like "how many", "yards", "distance", or specific counts mentioned.</instruction>
        <input>problem</input>
        <output>extracted_values</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Filter extracted values to match the exact question asked. For example, if the question asks about field goal yards, only keep entries that refer to field goals.</instruction>
        <input>extracted_values</input>
        <output>filtered_values</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Sum all relevant numeric values from the filtered list. If multiple entries exist (like multiple field goals), add them together for a total.</instruction>
        <input>filtered_values</input>
        <output>total</output>
    </node>
    
    <node id="5" type="output">
        <input>total</input>
    </node>