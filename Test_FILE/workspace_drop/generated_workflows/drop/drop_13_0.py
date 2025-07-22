# Workflow ID: drop_13_0
# Benchmark: drop
# Data Indices: [2913, 3501, 3526, 2635]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key question and relevant information in the passage. Think step by step to extract only what is necessary to answer the question.</instruction>
        <input>1</input>
        <output>processed_info</output>
    </node>
    <node id="3" type="agent">
        <instruction>For multi-part problems, determine if each sub-question can be solved independently. If so, process them separately to avoid unnecessary complexity.</instruction>
        <input>2</input>
        <output>sub_solutions</output>
    </node>
    <node id="4" type="agent">
        <instruction>Check for numerical comparisons or counts in the extracted data. If a direct comparison exists (e.g., percentages), use it to derive the answer without extra computation.</instruction>
        <input>3</input>
        <output>comparison_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>If multiple agents are needed for different parts of the problem, ensure each contributes uniquely to the final output. Do not duplicate logic.</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>