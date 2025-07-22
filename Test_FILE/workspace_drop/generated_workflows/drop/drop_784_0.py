# Workflow ID: drop_784_0
# Benchmark: drop
# Data Indices: [122, 888, 1730, 3678, 3340]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific values needed to answer the question, ensuring only relevant percentages or counts are used.</instruction>
        <input>extracted_data</input>
        <output>relevant_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Perform arithmetic operations (e.g., subtraction, percentage difference) using the relevant values.</instruction>
        <input>relevant_values</input>
        <output>calculation_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Format the result as a percentage point difference or appropriate unit based on the question.</instruction>
        <input>calculation_result</input>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <param name="answer" type="string"/>
        <input>final_answer</input>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>