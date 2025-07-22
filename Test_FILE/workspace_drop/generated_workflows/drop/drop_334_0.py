# Workflow ID: drop_334_0
# Benchmark: drop
# Data Indices: [642, 2099, 2750, 889]

<agent id="1">
        <instruction>Identify all field goals in the passage and extract their yardages.</instruction>
        <output>list of yardages</output>
    </agent>
    
    <agent id="2">
        <instruction>Filter the list to include only field goals of 30 yards or more.</instruction>
        <input>list of yardages from agent 1</input>
        <output>filtered list of yardages ≥ 30</output>
    </agent>
    
    <agent id="3">
        <instruction>Count the number of field goals in the filtered list.</instruction>
        <input>filtered list of yardages ≥ 30 from agent 2</input>
        <output>integer count</output>
    </agent>
    
    <agent id="4">
        <instruction>Verify that the count is correct by cross-checking against the original passage.</instruction>
        <input>integer count from agent 3</input>
        <output>final answer (integer)</output>
    </agent>
    
    <connect>
        <from>agent 1</from>
        <to>agent 2</to>
    </connect>
    
    <connect>
        <from>agent 2</from>
        <to>agent 3</to>
    </connect>
    
    <connect>
        <from>agent 3</from>
        <to>agent 4</to>
    </connect>