# Workflow ID: hotpotqa_234_0
# Benchmark: hotpotqa
# Data Indices: [1923, 198, 2821, 3826]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on extracting the main subject, the attribute being queried, and any relevant context.</instruction>
        <input>problem</input>
        <output>entity_and_context</output>
    </operator>
    <operator id="1">
        <instruction>Based on the extracted entity and context, determine which part of the provided context contains the answer to the question. Look for direct matches or logical inferences.</instruction>
        <input>entity_and_context</input>
        <output>candidate_answer</output>
    </operator>
    <operator id="2">
        <instruction>Verify that the candidate answer is consistent with the question's requirements and fully addresses the query without ambiguity.</instruction>
        <input>candidate_answer</input>
        <output>verified_answer</output>
    </operator>
    <operator id="3">
        <instruction>Ensure the final output is formatted as a single, clear response that directly answers the original question based on the verified information.</instruction>
        <input>verified_answer</input>
        <output>final_output</output>
    </operator>