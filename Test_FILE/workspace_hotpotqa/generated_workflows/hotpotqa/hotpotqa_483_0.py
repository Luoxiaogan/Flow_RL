# Workflow ID: hotpotqa_483_0
# Benchmark: hotpotqa
# Data Indices: [1581, 427, 2838, 3132]

<agent id="1">
        <instruction>Identify the key entities in the question and locate their relevant context.</instruction>
        <input>problem</input>
        <output>entity_context_mapping</output>
    </agent>
    <agent id="2">
        <instruction>Extract direct answers from the context for each entity, focusing on the core relationship asked in the question.</instruction>
        <input>entity_context_mapping</input>
        <output>candidate_answers</output>
    </agent>
    <agent id="3">
        <instruction>Verify each candidate answer against the full context to eliminate false positives or misinterpretations.</instruction>
        <input>candidate_answers</input>
        <output>verified_answers</output>
    </agent>
    <agent id="4">
        <instruction>Resolve any conflicts between verified answers by checking consistency with the question's intent and factual accuracy.</instruction>
        <input>verified_answers</input>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>