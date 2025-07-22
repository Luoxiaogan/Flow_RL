# Workflow ID: hotpotqa_284_0
# Benchmark: hotpotqa
# Data Indices: [2212, 1225, 519, 1642]

<agent id="1" type="extract">
        <instruction>Identify the key entities and relationships in the context. Focus on names, roles, and specific attributes mentioned.</instruction>
    </agent>
    <agent id="2" type="classify">
        <instruction>Classify each entity based on its domain (e.g., politics, entertainment, technology, etc.). Ensure accurate categorization for clarity.</instruction>
    </agent>
    <agent id="3" type="map">
        <instruction>Map the classified entities to their corresponding categories or attributes. Use cross-references from the context to build connections.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Verify that each mapping is consistent with the provided context. Remove any ambiguous or unsupported links.</instruction>
    </agent>
    <agent id="5" type="synthesize">
        <instruction>Combine validated mappings into a coherent structure. Highlight the most relevant information for answering the question.</instruction>
    </agent>
    <agent id="6" type="refine">
        <instruction>Refine the synthesized output by eliminating redundancy and focusing only on what directly answers the question.</instruction>
    </agent>
    <agent id="7" type="output">
        <instruction>Produce the final answer based on the refined synthesis. Ensure it's concise and directly addresses the query.</instruction>
    </agent>