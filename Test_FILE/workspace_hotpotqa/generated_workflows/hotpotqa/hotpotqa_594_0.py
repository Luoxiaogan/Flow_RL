# Workflow ID: hotpotqa_594_0
# Benchmark: hotpotqa
# Data Indices: [2437, 296, 276, 3013]

<start>
        <operator name="parse_input" />
        <operator name="validate_context" />
    </start>

    <operator name="parse_input">
        <input>problem</input>
        <output>parsed_question, parsed_context</output>
        <instruction>
            Analyze the input problem and extract the core question and relevant context. Focus on identifying key entities, relationships, and constraints.
        </instruction>
    </operator>

    <operator name="validate_context">
        <input>parsed_context</input>
        <output>valid_context</output>
        <instruction>
            Verify that the context contains sufficient information to answer the question. If not, flag for additional retrieval or indicate ambiguity.
        </instruction>
    </operator>

    <operator name="identify_key_entities">
        <input>parsed_question, valid_context</input>
        <output>entities</output>
        <instruction>
            Extract all named entities (people, works, dates, etc.) mentioned in both the question and context that are relevant to answering the query.
        </instruction>
    </operator>

    <operator name="map_relationships">
        <input>entities</input>
        <output>relationships</output>
        <instruction>
            Determine how the entities relate to each other—e.g., who composed what, who appeared in which movie, etc.—based on the context.
        </instruction>
    </operator>

    <operator name="generate_answer">
        <input>relationships</input>
        <output>answer</output>
        <instruction>
            Synthesize the mapped relationships into a concise, accurate answer that directly responds to the original question.
        </instruction>
    </operator>

    <operator name="verify_answer">
        <input>answer, parsed_question</input>
        <output>final_answer</output>
        <instruction>
            Cross-check the generated answer against the original question to ensure relevance, correctness, and completeness.
        </instruction>
    </operator>

    <end>
        <input>final_answer</input>
        <output>answer</output>
    </end>