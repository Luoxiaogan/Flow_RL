# Workflow ID: hotpotqa_376_0
# Benchmark: hotpotqa
# Data Indices: [3335, 1415, 1890, 145, 3191]

<operator id="0" type="agent">
        <instruction>Identify the key elements in the question and context that relate to the answer. Break down the problem into smaller components for analysis.</instruction>
    </operator>
    <operator id="1" type="agent">
        <instruction>For each component identified, determine if it directly answers the question or requires further investigation. If not, move to the next component.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Use logical reasoning to connect the components. Look for patterns, relationships, or direct references in the context that match the question.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify the connections made in the previous step by cross-referencing with the provided context. Eliminate any incorrect or unsupported links.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Formulate a concise answer based on the verified connections. Ensure it directly addresses the question without extraneous information.</instruction>
    </operator>
    <operator id="5" type="agent">
        <instruction>Review the final answer to ensure clarity, correctness, and completeness. Confirm it aligns with the question's intent and the evidence from the context.</instruction>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>