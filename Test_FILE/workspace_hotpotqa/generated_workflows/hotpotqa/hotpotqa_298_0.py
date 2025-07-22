# Workflow ID: hotpotqa_298_0
# Benchmark: hotpotqa
# Data Indices: [543, 3790, 693, 1861, 805]

<agent id="1" type="extract">
        <instruction>Extract the key entities and relationships from the context that are relevant to the question.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Reason step-by-step about how the extracted entities relate to the question. Identify which entity is the answer.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Validate the answer by cross-checking with the original context to ensure accuracy.</instruction>
    </agent>
    <agent id="4" type="refine">
        <instruction>Refine the final answer based on validation results, ensuring clarity and correctness.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />