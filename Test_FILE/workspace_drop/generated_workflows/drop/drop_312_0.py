# Workflow ID: drop_312_0
# Benchmark: drop
# Data Indices: [2263, 3419, 3760, 1979, 843]

<node id="1" type="input">
        <param name="problem" />
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the passage relevant to the question.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Extract numerical data or categorical comparisons from the passage that directly relate to the question.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Compare the extracted values to determine which group is larger or smaller based on the question's focus.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="agent">
        <instruction>Formulate a concise answer based on the comparison, ensuring it directly addresses the question.</instruction>
        <input>4</input>
    </node>
    <node id="6" type="output">
        <input>5</input>
    </node>