# Workflow ID: hotpotqa_297_0
# Benchmark: hotpotqa
# Data Indices: [1594, 2807, 19, 3366]

<operator id="1" type="extract">
        <input>problem</input>
        <output>extracted_context</output>
        <prompt>Identify the key entities and their relationships in the problem context. Focus on explicit connections between subjects, events, or concepts.</prompt>
    </operator>
    
    <operator id="2" type="analyze">
        <input>extracted_context</input>
        <output>structured_data</output>
        <prompt>Break down the extracted context into structured elements: subject, attribute, value. Ensure each element is atomic and logically distinct.</prompt>
    </operator>
    
    <operator id="3" type="map">
        <input>structured_data</input>
        <output>relationship_graph</output>
        <prompt>Map each structured element to a node and define edges based on logical or contextual dependencies. Avoid redundant links.</prompt>
    </operator>
    
    <operator id="4" type="validate">
        <input>relationship_graph</input>
        <output>validated_graph</output>
        <prompt>Check for consistency: all nodes must have at least one edge, no isolated nodes, and all attributes must be grounded in the original context.</prompt>
    </operator>
    
    <operator id="5" type="optimize">
        <input>validated_graph</input>
        <output>optimized_graph</output>
        <prompt>Reduce graph complexity by merging redundant nodes or simplifying paths while preserving semantic meaning. Target 3–8 nodes.</prompt>
    </operator>
    
    <operator id="6" type="verify">
        <input>optimized_graph</input>
        <output>final_output</output>
        <prompt>Ensure the final graph contains exactly one answer node that directly resolves the question. All other nodes must support it.</prompt>
    </operator>