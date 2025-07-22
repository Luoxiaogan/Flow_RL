# Workflow ID: drop_136_0
# Benchmark: drop
# Data Indices: [192, 2139, 1018, 67, 2737]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data and percentages in the passage relevant to the question.</instruction>
        <input>1</input>
        <output>2</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform arithmetic operations (e.g., subtraction, percentage calculation) based on the identified data to answer the specific question.</instruction>
        <input>2</input>
        <output>3</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the result by cross-checking with the original passage to ensure accuracy and logical consistency.</instruction>
        <input>3</input>
        <output>4</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <param name="final_answer">result</param>
    </node>