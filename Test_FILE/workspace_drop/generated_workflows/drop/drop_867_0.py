# Workflow ID: drop_867_0
# Benchmark: drop
# Data Indices: [1215, 2569, 3372, 2167]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that pertains to the question.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform necessary calculations or comparisons based on the extracted data to answer the question step by step.</instruction>
        <input>2</input>
        <output>calculated_result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Validate the result by cross-checking with the original passage and ensuring logical consistency.</instruction>
        <input>3</input>
        <output>validated_result</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>