# Workflow ID: hotpotqa_441_0
# Benchmark: hotpotqa
# Data Indices: [1309, 989, 2190, 3737]

<operator id="0" type="extract">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on the main subject, associated objects, and their connections.</instruction>
    </operator>
    <operator id="1" type="reason">
        <instruction>Step-by-step reasoning: First, determine which entity is directly relevant to the question. Then, trace back through the context to find supporting evidence or related facts that confirm the answer.</instruction>
    </operator>
    <operator id="2" type="validate">
        <instruction>Check if the extracted information from the context supports the derived answer. If multiple sources exist, ensure consistency across them.</instruction>
    </operator>
    <operator id="3" type="combine">
        <instruction>Integrate validated results from all relevant operators into a single coherent response. Ensure no contradictions exist between steps.</instruction>
    </operator>
    <operator id="4" type="final">
        <instruction>Output the final answer based on the combined result. Do not include any intermediate reasoning or extra text.</instruction>
    </operator>