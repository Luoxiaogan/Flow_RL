# Workflow ID: drop_552_0
# Benchmark: drop
# Data Indices: [3193, 3920, 2288, 3176]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points in the passage relevant to the question. Focus on specific values, such as scores, percentages, or distances mentioned.</instruction>
        <input>problem</input>
        <output>key_data_points</output>
    </node>
    <node id="3" type="agent">
        <instruction>Extract and isolate the exact value that answers the question from the key data points. Ensure no extra information is included.</instruction>
        <input>key_data_points</input>
        <output>answer_value</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the extracted value matches the question's requirement exactly—e.g., units, context, and precision.</instruction>
        <input>answer_value</input>
        <output>validated_answer</output>
    </node>
    <node id="5" type="output">
        <input>validated_answer</input>
    </node>