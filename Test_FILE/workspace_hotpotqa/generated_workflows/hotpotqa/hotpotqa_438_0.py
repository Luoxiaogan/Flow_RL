# Workflow ID: hotpotqa_438_0
# Benchmark: hotpotqa
# Data Indices: [567, 4, 3821, 2125, 1950]

<operator id="1" type="agent">
        <instruction>Think step by step to identify the key entities and relationships in the problem. Extract all relevant names, dates, and facts that could help answer the question.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Compare the extracted data to determine which entity matches the criteria specified in the question. Focus on chronological order, chart positions, or other specific attributes mentioned.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify the match by cross-referencing with known facts from the context. Ensure no ambiguity remains between similar-sounding names or events.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Generate a concise answer based on the verified match. Do not include extra details unless explicitly asked.</instruction>
    </operator>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>