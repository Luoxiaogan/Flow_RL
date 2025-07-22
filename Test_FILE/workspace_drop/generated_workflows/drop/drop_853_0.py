# Workflow ID: drop_853_0
# Benchmark: drop
# Data Indices: [523, 722, 272, 1112, 3581]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract key numerical data from the passage relevant to the question. Identify all percentages, yard lines, or scores mentioned.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>For Problem 1: Compare the percentages of agriculture, industry, and services to determine the smallest. For Problems 2-5: Extract specific yard line or play details for each touchdown or final play.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Validate that the extracted values are directly tied to the question asked. Discard any irrelevant data such as unrelated stats or general context.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="agent">
        <instruction>Format the final answer clearly based on the validated data. Ensure it matches the exact requirement of the question (e.g., "agriculture", "42 yards", etc.).</instruction>
        <input>4</input>
    </node>
    <node id="6" type="output">
        <data>final_answer</data>
        <input>5</input>
    </node>