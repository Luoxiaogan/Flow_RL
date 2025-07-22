# Workflow ID: hotpotqa_11_0
# Benchmark: hotpotqa
# Data Indices: [3687, 617, 1719, 1870]

<agent id="1" type="question_analysis">
        <instruction>Break down the question into key components: identify the subject, the specific information requested, and any relevant context clues.</instruction>
    </agent>
    <agent id="2" type="context_identification">
        <instruction>Scan the provided context for entities directly related to the subject and the requested information. Extract only the relevant details that connect the subject to the answer.</instruction>
    </agent>
    <agent id="3" type="entity_resolution">
        <instruction>Resolve ambiguous references by matching extracted context to known facts—e.g., confirm identities, timelines, or relationships between people mentioned.</instruction>
    </agent>
    <agent id="4" type="fact_verification">
        <instruction>Verify the extracted fact against multiple pieces of context to ensure accuracy and avoid contradictions.</instruction>
    </agent>
    <agent id="5" type="answer_formulation">
        <instruction>Construct a clear, concise answer based on the verified fact. Ensure it directly addresses the original question without adding unsupported details.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>