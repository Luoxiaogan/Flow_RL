# Workflow ID: drop_149_0
# Benchmark: drop
# Data Indices: [955, 2328, 1541, 3729]

<node id="1" type="input">
        <param>problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data in the passage relevant to the question. Focus on specific events, scores, or statistics mentioned.</instruction>
        <input>1</input>
        <output>key_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Extract and isolate the values that directly answer the question. If multiple values are needed, ensure they are correctly grouped by category (e.g., field goals, touchdowns, etc.).</instruction>
        <input>2</input>
        <output>extracted_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary calculation based on the extracted values. For example, sum field goal distances or count touchdowns within a range.</instruction>
        <input>3</input>
        <output>calculation_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the result matches the question's requirements exactly—no extra information, no missing steps. Ensure clarity and correctness.</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <param>final_answer</param>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>