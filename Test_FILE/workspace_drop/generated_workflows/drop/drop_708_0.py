# Workflow ID: drop_708_0
# Benchmark: drop
# Data Indices: [1723, 3383, 2991, 2718, 3470]

<node id="1">
        <instruction>Identify the key event or action mentioned in the question.</instruction>
        <next>2</next>
    </node>
    <node id="2">
        <instruction>Extract relevant details from the passage that relate to the identified event.</instruction>
        <next>3</next>
    </node>
    <node id="3">
        <instruction>Determine if the passage contains a direct answer or requires inference based on sequence, count, or calculation.</instruction>
        <next>4</next>
    </node>
    <node id="4">
        <instruction>If inference is needed, apply logical reasoning using the extracted facts (e.g., order of events, numerical totals).</instruction>
        <next>5</next>
    </node>
    <node id="5">
        <instruction>Verify that the inferred or direct answer matches the question’s requirement exactly.</instruction>
        <next>6</next>
    </node>
    <node id="6">
        <instruction>Output the final answer as a concise, correct response.</instruction>
        <next>end</next>
    </node>