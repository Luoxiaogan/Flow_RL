# Workflow ID: drop_288_0
# Benchmark: drop
# Data Indices: [764, 2451, 2806, 248]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific category or group mentioned in the question from the extracted data.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary calculation or comparison to determine the answer based on the identified category.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the result aligns with the question's requirements and is derived solely from the passage.</instruction>
    </node>
    <node id="6" type="output">
        <data>final_answer</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>