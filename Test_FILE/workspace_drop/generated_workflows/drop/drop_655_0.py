# Workflow ID: drop_655_0
# Benchmark: drop
# Data Indices: [798, 1772, 1701, 2378, 3069]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the problem step by step to identify the key numerical data needed for the answer.
        </instruction>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Determine which values in the extracted data are relevant to the question asked.
        </instruction>
        <output>relevant_values</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Perform necessary calculations or comparisons using the relevant values.
        </instruction>
        <output>computed_result</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>
            Verify that the computed result matches the question's requirement and format it correctly.
        </instruction>
        <output>final_answer</output>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>