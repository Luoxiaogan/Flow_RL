# Workflow ID: drop_607_0
# Benchmark: drop
# Data Indices: [993, 137, 544, 2618, 287]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract the relevant numerical data from the passage that answers the question. Focus on the specific values mentioned in the context of the question.</instruction>
        <input>1</input>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify which group in the census has a higher percentage: Asian or African American. Compare the percentages directly from the extracted data.</instruction>
        <input>2</input>
    </node>
    
    <node id="4" type="agent">
        <instruction>Determine the larger group based on the comparison. Return 'Asian' if its percentage is higher, otherwise return 'African American'.</instruction>
        <input>3</input>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
    </node>