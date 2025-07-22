# Workflow ID: hotpotqa_540_0
# Benchmark: hotpotqa
# Data Indices: [1926, 264, 1104, 1399, 1386]

<agent id="1" type="extract">
        <instruction>Extract the key entities and relationships from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Reason step by step: Identify the main subject, determine the correct answer based on extracted facts, and verify consistency with the context.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Validate the answer by cross-checking against all provided context details. Ensure no contradictions exist.</instruction>
    </agent>
    <agent id="4" type="output">
        <instruction>Generate the final output in the required format, ensuring clarity and correctness.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>