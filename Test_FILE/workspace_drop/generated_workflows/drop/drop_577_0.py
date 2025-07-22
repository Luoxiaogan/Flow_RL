# Workflow ID: drop_577_0
# Benchmark: drop
# Data Indices: [2094, 1348, 3845, 2321, 3492]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage. Identify the quantities mentioned in the problem context.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Perform necessary arithmetic operations based on the extracted data to answer the question step by step.</instruction>
        <input>2</input>
        <output>calculation_result</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the calculation aligns with the question and ensures no misinterpretation of the original text.</instruction>
        <input>3</input>
        <output>verification_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Format the final answer clearly, ensuring it matches the exact query asked in the question.</instruction>
        <input>4</input>
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