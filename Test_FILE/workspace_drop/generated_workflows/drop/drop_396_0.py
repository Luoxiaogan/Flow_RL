# Workflow ID: drop_396_0
# Benchmark: drop
# Data Indices: [3653, 3928, 1621, 2067]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the key numerical data in the passage relevant to the question. Extract percentages, counts, or specific values mentioned.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Map the extracted data to the specific question being asked. Determine which value directly answers the query.</instruction>
        <input>2</input>
        <output>mapped_value</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that the mapped value is consistent with the context of the question and the passage. If ambiguous, flag for review.</instruction>
        <input>3</input>
        <output>verified_answer</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>