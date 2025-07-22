# Workflow ID: hotpotqa_504_0
# Benchmark: hotpotqa
# Data Indices: [195, 2859, 3829, 67]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem statement. Break down the question to isolate the main subject and the required answer.</instruction>
        <input>problem</input>
        <output>structured_query</output>
    </operator>
    <operator id="2">
        <instruction>Search for direct matches or relevant context in the provided materials that link the subject to the answer. Focus on explicit mentions of roles, names, and events.</instruction>
        <input>structured_query</input>
        <output>candidate_answer</output>
    </operator>
    <operator id="3">
        <instruction>Validate the candidate answer by cross-referencing with supporting evidence from the context. Ensure no ambiguity remains.</instruction>
        <input>candidate_answer</input>
        <output>validated_answer</output>
    </operator>
    <operator id="4">
        <instruction>Format the final output as a concise, clear response based on the validated answer. Avoid unnecessary details.</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </operator>