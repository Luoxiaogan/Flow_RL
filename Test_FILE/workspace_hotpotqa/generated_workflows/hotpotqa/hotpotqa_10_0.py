# Workflow ID: hotpotqa_10_0
# Benchmark: hotpotqa
# Data Indices: [622, 3967, 3979, 2472, 1245]

<agent id="1" type="question_analysis">
        <instruction>Break down the question to identify key entities and relationships. Focus on extracting the main subject and what is being asked about them.</instruction>
    </agent>
    <agent id="2" type="context_retrieval">
        <instruction>Scan the provided context for mentions of the key entity identified in step 1. Locate all relevant passages that may contain the answer.</instruction>
    </agent>
    <agent id="3" type="entity_validation">
        <instruction>Verify that the candidate answer from step 2 matches the question's requirements. Cross-check dates, names, and roles to ensure accuracy.</instruction>
    </agent>
    <agent id="4" type="answer_synthesis">
        <instruction>Combine validated information into a concise, accurate response. Ensure the final output directly answers the original question without extra details.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>