# Workflow ID: drop_543_0
# Benchmark: drop
# Data Indices: [2597, 3067, 2236, 358]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    <node id="2" type="agent">
        <instruction>
            Analyze the problem statement and identify the key numerical values or time periods mentioned.
        </instruction>
        <input>1</input>
        <output>2</output>
    </node>
    <node id="3" type="agent">
        <instruction>
            Extract relevant data points from the passage that directly answer the question. For example, find start year and death year for Problem 1, or specific scores for Problem 3.
        </instruction>
        <input>2</input>
        <output>3</output>
    </node>
    <node id="4" type="agent">
        <instruction>
            Perform necessary arithmetic or comparison operations based on extracted values (e.g., subtract years, compare scores).
        </instruction>
        <input>3</input>
        <output>4</output>
    </node>
    <node id="5" type="agent">
        <instruction>
            Verify the result by cross-checking with original passage to ensure accuracy.
        </instruction>
        <input>4</input>
        <output>5</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>