# Workflow ID: drop_734_0
# Benchmark: drop
# Data Indices: [1066, 1715, 2715, 1240, 274]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that directly answers the question.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Perform necessary calculations using the extracted data to derive the answer.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the calculation by cross-checking with the passage context to ensure accuracy.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>