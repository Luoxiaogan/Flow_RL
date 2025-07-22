# Workflow ID: hotpotqa_503_0
# Benchmark: hotpotqa
# Data Indices: [1849, 3452, 2607, 1869]

<agent id="1">
        <instruction>Identify the key entity in the question and locate its corresponding context.</instruction>
        <input>problem</input>
        <output>entity, context_segment</output>
    </agent>
    <agent id="2">
        <instruction>Extract relevant information from the context that directly answers the question.</instruction>
        <input>entity, context_segment</input>
        <output>candidate_answer</output>
    </agent>
    <agent id="3">
        <instruction>Verify the candidate answer against all available context to ensure accuracy.</instruction>
        <input>candidate_answer, context_segment</input>
        <output>final_answer</output>
    </agent>
    <agent id="4">
        <instruction>Validate the final answer by cross-referencing with known facts or alternative sources if available.</instruction>
        <input>final_answer</input>
        <output>validated_answer</output>
    </agent>
    <agent id="5">
        <instruction>Ensure the validated answer is consistent with the question's intent and format requirements.</instruction>
        <input>validated_answer</input>
        <output>formatted_answer</output>
    </agent>
    <agent id="6">
        <instruction>Generate a concise explanation of how the answer was derived, step-by-step.</instruction>
        <input>formatted_answer, agent_outputs</input>
        <output>explanation</output>
    </agent>
    <link from="1" to="2"/>
    <link from="2" to="3"/>
    <link from="3" to="4"/>
    <link from="4" to="5"/>
    <link from="5" to="6"/>