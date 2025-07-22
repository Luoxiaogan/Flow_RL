# Workflow ID: drop_665_0
# Benchmark: drop
# Data Indices: [1693, 2833, 3433, 2599, 731]

<node id="1" type="input">
        <prompt>Extract the relevant numerical data from the passage to solve the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify the key values needed to answer the question based on the extracted data.</prompt>
    </node>
    <node id="3" type="compute">
        <prompt>Perform the necessary mathematical operation (e.g., subtraction, comparison) using the identified values.</prompt>
    </node>
    <node id="4" type="validate">
        <prompt>Verify that the computed result matches the context of the question and is logically sound.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer in a clear and concise format.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>