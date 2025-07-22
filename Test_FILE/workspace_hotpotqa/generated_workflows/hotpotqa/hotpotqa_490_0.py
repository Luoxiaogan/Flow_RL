# Workflow ID: hotpotqa_490_0
# Benchmark: hotpotqa
# Data Indices: [2928, 576, 1220, 3694, 1387]

<agent id="1" type="extract">
        <instruction>Identify the key entities and relationships in the context that are relevant to the question. Focus on extracting only the necessary information to answer the question.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>From the extracted information, filter out details that are not directly related to the specific question. Keep only the facts that help determine the correct answer.</instruction>
    </agent>
    <agent id="3" type="reason">
        <instruction>Use the filtered information to reason step-by-step. Determine how each piece of data contributes to answering the question logically.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Verify the logical consistency of your reasoning. Ensure that no assumptions are made beyond what is explicitly stated in the context.</instruction>
    </agent>
    <agent id="5" type="assemble">
        <instruction>Combine the validated reasoning into a clear, concise final answer. Make sure it directly addresses the question without extra or missing details.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>