# Workflow ID: drop_262_0
# Benchmark: drop
# Data Indices: [2029, 1938, 1174, 40, 1102]

<node id="1" type="input">
        <prompt>Understand the question and identify the key information needed to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant numerical or categorical data from the passage that directly answers the question. Think step by step: first identify what is being asked, then locate the exact numbers or facts in the text.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Perform necessary calculations or comparisons using the extracted data. If multiple values are involved, determine which one is the correct answer based on the question's requirement.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that your answer matches the format required (e.g., number, year, count). Ensure no extraneous details are included.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return only the final answer as a concise value or string, matching the question's expected output type.</prompt>
    </node>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>