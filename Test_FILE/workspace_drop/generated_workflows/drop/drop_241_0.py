# Workflow ID: drop_241_0
# Benchmark: drop
# Data Indices: [510, 773, 2503, 1870, 1280]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that relates to the question.</instruction>
        <param name="input">1</param>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific values needed to answer the question based on the extracted data.</instruction>
        <param name="input">2</param>
        <output>target_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary calculations using the target values to derive the answer.</instruction>
        <param name="input">3</param>
        <output>calculated_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the correctness of the calculated result by cross-checking with the original passage context.</instruction>
        <param name="input">4</param>
        <output>verified_result</output>
    </node>
    <node id="6" type="output">
        <param name="input">5</param>
        <param name="format">final_answer</param>
    </node>