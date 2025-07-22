# Workflow ID: hotpotqa_77_0
# Benchmark: hotpotqa
# Data Indices: [930, 288, 2623, 2371, 999]

<operator id="1" type="extract">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on the main subject, the associated attributes, and any relevant context.</instruction>
    </operator>
    <operator id="2" type="filter">
        <instruction>From the extracted entities, filter out only those that are directly relevant to answering the question. Discard any extraneous or ambiguous information.</instruction>
    </operator>
    <operator id="3" type="map">
        <instruction>Map the filtered entities to known facts or patterns in the provided context. Look for direct matches or logical connections between the question and available data.</instruction>
    </operator>
    <operator id="4" type="reason">
        <instruction>Use the mapped relationships to reason step-by-step toward the correct answer. If multiple candidates exist, apply constraints from the question to narrow them down.</instruction>
    </operator>
    <operator id="5" type="validate">
        <instruction>Verify that the derived answer satisfies all conditions of the question. Cross-check against the original problem and context to ensure accuracy and completeness.</instruction>
    </operator>
    <operator id="6" type="output">
        <instruction>Format the final answer clearly and concisely, ensuring it directly addresses the question without unnecessary elaboration.</instruction>
    </operator>