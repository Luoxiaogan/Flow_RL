# Workflow ID: hotpotqa_456_0
# Benchmark: hotpotqa
# Data Indices: [3015, 36, 2552, 3891]

<agent id="1">
        <instruction>Identify the key subject in the question and locate related context information.</instruction>
        <input>problem</input>
        <output>subject_info</output>
    </agent>
    <agent id="2">
        <instruction>Extract the relevant entity (e.g., person, book, event) from the context that directly answers the question.</instruction>
        <input>subject_info</input>
        <output>entity</output>
    </agent>
    <agent id="3">
        <instruction>Verify the extracted entity matches the question's requirement by cross-referencing with known facts or additional context.</instruction>
        <input>entity</input>
        <output>verification_result</output>
    </agent>
    <agent id="4">
        <instruction>Generate the final answer based on verified entity, ensuring it is concise and directly addresses the question.</instruction>
        <input>verification_result</input>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>