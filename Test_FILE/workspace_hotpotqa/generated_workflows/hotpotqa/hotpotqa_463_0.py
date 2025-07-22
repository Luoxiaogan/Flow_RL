# Workflow ID: hotpotqa_463_0
# Benchmark: hotpotqa
# Data Indices: [1379, 234, 148, 459]

<operator id="0">
        <instruction>Identify the key entities in the problem and determine the specific information being asked.</instruction>
        <input>problem</input>
        <output>key_entities, question_focus</output>
    </operator>
    <operator id="1">
        <instruction>Extract all relevant context that might contain the answer to the question.</instruction>
        <input>context</input>
        <output>relevant_context</output>
    </operator>
    <operator id="2">
        <instruction>Match the question focus with the relevant context to isolate potential answers.</instruction>
        <input>question_focus, relevant_context</input>
        <output>candidate_answers</output>
    </operator>
    <operator id="3">
        <instruction>Validate each candidate answer by cross-referencing with other known facts or logical constraints from the context.</instruction>
        <input>candidate_answers, context</input>
        <output>validated_answers</output>
    </operator>
    <operator id="4">
        <instruction>Rank the validated answers based on specificity, uniqueness, and direct relevance to the question.</instruction>
        <input>validated_answers</input>
        <output>ranked_answers</output>
    </operator>
    <operator id="5">
        <instruction>Return the top-ranked answer as the final solution.</instruction>
        <input>ranked_answers</input>
        <output>final_answer</output>
    </operator>