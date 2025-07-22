# Workflow ID: hotpotqa_468_0
# Benchmark: hotpotqa
# Data Indices: [1595, 1411, 750, 3585]

<node id="start" type="input">
        <prompt>Begin processing the input problem.</prompt>
    </node>
    
    <node id="analyze_context" type="agent">
        <prompt>Step 1: Analyze the context provided to identify relevant keywords, entities, and relationships. Focus on extracting only what is directly needed for answering the question. Avoid overcomplication or irrelevant details.</prompt>
    </node>
    
    <node id="identify_key_concepts" type="agent">
        <prompt>Step 2: From the analyzed context, identify key concepts that are central to solving the problem. These should include specific terms, names, dates, or categories that match the question's focus.</prompt>
    </node>
    
    <node id="map_to_solution" type="agent">
        <prompt>Step 3: Map the identified key concepts to potential answers. If multiple options exist, evaluate each against the question’s specificity to determine which best fits the required output format (e.g., a date, name, term).</prompt>
    </node>
    
    <node id="validate_output" type="agent">
        <prompt>Step 4: Validate that the selected answer logically follows from the context and satisfies the question. Ensure no external assumptions are introduced—only use information explicitly present in the context.</prompt>
    </node>
    
    <node id="output_result" type="output">
        <prompt>Final output: Return the validated answer in a clear, concise format as per the task requirements.</prompt>
    </node>
    
    <edge from="start" to="analyze_context"/>
    <edge from="analyze_context" to="identify_key_concepts"/>
    <edge from="identify_key_concepts" to="map_to_solution"/>
    <edge from="map_to_solution" to="validate_output"/>
    <edge from="validate_output" to="output_result"/>