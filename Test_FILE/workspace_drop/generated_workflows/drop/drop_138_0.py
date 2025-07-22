# Workflow ID: drop_138_0
# Benchmark: drop
# Data Indices: [2760, 2805, 148, 1158]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical question in the passage and extract the relevant data.</instruction>
        <input>1</input>
        <output>2</output>
    </node>
    <node id="3" type="agent">
        <instruction>Verify the extracted number by cross-referencing with other parts of the passage to ensure accuracy.</instruction>
        <input>2</input>
        <output>3</output>
    </node>
    <node id="4" type="agent">
        <instruction>Check if the answer matches the exact wording of the question (e.g., "how many years", "how many points").</instruction>
        <input>3</input>
        <output>4</output>
    </node>
    <node id="5" type="agent">
        <instruction>Ensure the final answer is a single integer, no extra text or formatting.</instruction>
        <input>4</input>
        <output>5</output>
    </node>
    <node id="6" type="agent">
        <instruction>Validate that the solution process does not introduce any external assumptions or missing context from the passage.</instruction>
        <input>5</input>
        <output>6</output>
    </node>
    <node id="7" type="output">
        <data>6</data>
    </node>