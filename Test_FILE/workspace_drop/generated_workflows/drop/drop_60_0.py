# Workflow ID: drop_60_0
# Benchmark: drop
# Data Indices: [2282, 972, 931, 3553]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Think step by step: Identify the relevant information in the passage that answers the question. Extract numerical values associated with the entities mentioned in the question.
        </instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Think step by step: Determine which values correspond to the entities in the question. Calculate the difference between the two values if required.
        </instruction>
        <input>2</input>
        <output>calculated_difference</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Think step by step: Verify that the calculation is correct and matches the question. Ensure no irrelevant data was used.
        </instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
    </node>