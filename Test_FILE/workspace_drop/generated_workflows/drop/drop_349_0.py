# Workflow ID: drop_349_0
# Benchmark: drop
# Data Indices: [2980, 1816, 82, 3494]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that relates to the question.</instruction>
        <input>1</input>
        <output>3</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific values or percentages needed to answer the question, ensuring no irrelevant data is included.</instruction>
        <input>2</input>
        <output>4</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary arithmetic operations (e.g., subtraction, division) to compute the final answer based on extracted values.</instruction>
        <input>3</input>
        <output>5</output>
    </node>
    <node id="5" type="output">
        <param name="answer" type="float"/>
        <input>4</input>
    </node>