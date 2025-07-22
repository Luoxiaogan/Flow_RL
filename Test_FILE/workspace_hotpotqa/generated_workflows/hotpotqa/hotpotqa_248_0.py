# Workflow ID: hotpotqa_248_0
# Benchmark: hotpotqa
# Data Indices: [794, 2837, 3351, 3661, 1877]

<node id="start" type="input">
        <prompt>Begin processing the problem by identifying key entities and relationships in the context.</prompt>
    </node>
    
    <node id="analyze_context" type="agent">
        <prompt>Extract relevant information from the context that directly answers the question. Focus on specific names, dates, and events mentioned.</prompt>
    </node>
    
    <node id="verify_relevance" type="agent">
        <prompt>Check if the extracted information is directly relevant to the question. Discard any tangential or indirect details.</prompt>
    </node>
    
    <node id="validate_date" type="agent">
        <prompt>Confirm the correctness of the date by cross-referencing with other known facts in the context or external knowledge if necessary.</prompt>
    </node>
    
    <node id="generate_answer" type="agent">
        <prompt>Construct a clear and concise answer based on the validated information. Ensure it directly addresses the question asked.</prompt>
    </node>
    
    <node id="end" type="output">
        <prompt>Final output: Return the correct answer as derived from the previous steps.</prompt>
    </node>

    <!-- Edges -->
    <edge from="start" to="analyze_context"/>
    <edge from="analyze_context" to="verify_relevance"/>
    <edge from="verify_relevance" to="validate_date"/>
    <edge from="validate_date" to="generate_answer"/>
    <edge from="generate_answer" to="end"/>