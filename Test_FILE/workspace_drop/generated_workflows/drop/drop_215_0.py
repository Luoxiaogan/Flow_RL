# Workflow ID: drop_215_0
# Benchmark: drop
# Data Indices: [2447, 1442, 3180, 1447, 3064]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that can help answer the question. Identify key entities, values, and relationships.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific comparison or calculation required to answer the question. Determine which values need to be compared or operated on.</instruction>
        <input>2</input>
        <output>comparison_logic</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic or logical operation based on the extracted data and comparison logic. Ensure precision in calculations.</instruction>
        <input>3</input>
        <output>result</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Verify the result by cross-checking against the original passage for consistency and correctness of interpretation.</instruction>
        <input>4</input>
        <output>verified_result</output>
    </node>
    
    <node id="6" type="output">
        <input>5</input>
        <output>final_answer</output>
    </node>