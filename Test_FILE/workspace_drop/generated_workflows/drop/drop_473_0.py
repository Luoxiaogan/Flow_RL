# Workflow ID: drop_473_0
# Benchmark: drop
# Data Indices: [3185, 741, 1592, 2201, 1568]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract all relevant numerical data from the passage related to the question. Identify entities, values, and their relationships.</instruction>
        <input>1</input>
        <output>2</output>
    </node>
    <node id="3" type="agent">
        <instruction>For each entity mentioned in the question, locate its corresponding value(s) in the extracted data. If multiple values exist, determine which one(s) are relevant based on context.</instruction>
        <input>2</input>
        <output>3</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary arithmetic or logical operations to derive the final answer. For example, compute differences, sums, or comparisons between values.</instruction>
        <input>3</input>
        <output>4</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the computed answer matches the question's requirement exactly—no extra information, no missing details.</instruction>
        <input>4</input>
        <output>5</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>