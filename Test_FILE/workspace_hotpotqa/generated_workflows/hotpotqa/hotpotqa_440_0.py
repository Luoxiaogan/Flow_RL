# Workflow ID: hotpotqa_440_0
# Benchmark: hotpotqa
# Data Indices: [650, 2919, 3873, 3958, 760]

<start>
        <task>Identify the key entities in the problem context</task>
        <next>extract_entities</next>
    </start>

    <node id="extract_entities">
        <task>Extract relevant named entities (people, places, events) from the context</task>
        <next>match_entities_to_question</next>
    </node>

    <node id="match_entities_to_question">
        <task>Map extracted entities to the question's focus (e.g., person, event, object)</task>
        <next>validate_context_relevance</next>
    </node>

    <node id="validate_context_relevance">
        <task>Verify that the matched entities directly answer the question</task>
        <next>generate_answer</next>
    </node>

    <node id="generate_answer">
        <task>Construct a concise and accurate answer based on validated context</task>
        <next>end</next>
    </node>

    <end>
        <output>Final answer</output>
    </end>