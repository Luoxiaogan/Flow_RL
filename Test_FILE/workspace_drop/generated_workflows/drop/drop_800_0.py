# Workflow ID: drop_800_0
# Benchmark: drop
# Data Indices: [2027, 839, 165, 3198]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical values related to the question in the passage. Focus on extracting only the relevant numbers and their context.</instruction>
        <input>problem</input>
        <output>extracted_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>For each extracted value, determine its role in answering the question. Classify whether it is a base value, comparison value, or irrelevant.</instruction>
        <input>extracted_values</input>
        <output>classified_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Apply the correct arithmetic operation based on the classification: subtraction for "how many more", addition for totals, etc.</instruction>
        <input>classified_values</input>
        <output>calculated_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Verify that the result aligns with the question's phrasing and that no steps were skipped or misinterpreted.</instruction>
        <input>calculated_result</output>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <parameter>final_answer</parameter>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>