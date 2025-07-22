# Workflow ID: drop_317_0
# Benchmark: drop
# Data Indices: [2040, 1920, 3697, 1735, 1031]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the key numerical values and relationships in the passage relevant to the question. Break down the problem step by step.</instruction>
        <input>1</input>
    </node>
    
    <node id="3" type="agent">
        <instruction>Apply mathematical or logical operations based on the extracted data to compute the required result. Ensure accuracy in calculations.</instruction>
        <input>2</input>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify the computed answer against the context of the passage to ensure it aligns with the question's requirements.</instruction>
        <input>3</input>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
    </node>