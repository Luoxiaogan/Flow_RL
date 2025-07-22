# Workflow ID: hotpotqa_26_0
# Benchmark: hotpotqa
# Data Indices: [147, 482, 1592, 3123]

<operator id="0" type="extract">
        <prompt>Extract the key entities and relationships from the context provided.</prompt>
    </operator>
    <operator id="1" type="map">
        <prompt>Map each entity to its relevant category (e.g., person, film, award, country).</prompt>
    </operator>
    <operator id="2" type="filter">
        <prompt>Filter out irrelevant information that does not pertain to the question.</prompt>
    </operator>
    <operator id="3" type="relate">
        <prompt>Identify direct or indirect relationships between entities based on the filtered context.</prompt>
    </operator>
    <operator id="4" type="infer">
        <prompt>Use logical inference to deduce the answer based on the relationships established.</prompt>
    </operator>
    <operator id="5" type="validate">
        <prompt>Validate the inferred answer against the original context for consistency.</prompt>
    </operator>
    <operator id="6" type="output">
        <prompt>Output the final answer in a clear and concise format.</prompt>
    </operator>