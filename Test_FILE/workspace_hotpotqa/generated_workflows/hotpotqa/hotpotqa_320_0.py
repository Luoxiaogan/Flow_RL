# Workflow ID: hotpotqa_320_0
# Benchmark: hotpotqa
# Data Indices: [299, 611, 2520, 3977, 1094]

<start/>
    <agent id="1" type="extract">
        <instruction>Extract the key entities and relationships from the context provided.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Reason through the extracted information to identify which entity directly answers the question.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Validate that the answer is consistent with all relevant context clues and does not contradict any facts.</instruction>
    </agent>
    <agent id="4" type="synthesize">
        <instruction>Combine the validated result into a clear, concise final answer.</instruction>
    </agent>
    <end/>
    <edge from="start" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="end"/>