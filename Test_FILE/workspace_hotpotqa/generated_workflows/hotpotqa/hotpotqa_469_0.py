# Workflow ID: hotpotqa_469_0
# Benchmark: hotpotqa
# Data Indices: [2051, 795, 3720, 2686]

<agent id="1">
        <instruction>Identify the key entities and relationships in the problem context. Focus on extracting structured data points relevant to the question.</instruction>
        <output>Structured data points extracted from context</output>
    </agent>
    <agent id="2">
        <instruction>Map the extracted data points to potential answers by matching keywords and contextual clues in the question.</instruction>
        <output>Potential answer candidates with confidence scores</output>
    </agent>
    <agent id="3">
        <instruction>Validate each candidate against the full context to eliminate false positives or ambiguous matches.</instruction>
        <output>Validated answer candidates</output>
    </agent>
    <agent id="4">
        <instruction>Apply logical reasoning to resolve conflicts between candidates, prioritizing consistency with the most specific and direct evidence.</instruction>
        <output>Final answer with justification</output>
    </agent>
    <link from="1" to="2"/>
    <link from="2" to="3"/>
    <link from="3" to="4"/>