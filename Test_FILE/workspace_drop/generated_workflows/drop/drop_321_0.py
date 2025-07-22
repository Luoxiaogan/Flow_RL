# Workflow ID: drop_321_0
# Benchmark: drop
# Data Indices: [3988, 2314, 3318, 2388]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the problem and identify the key numerical data points relevant to the question.
        </instruction>
        <input>1</input>
        <output>key_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Extract all relevant values from the passage that can be used to compute the answer. For example, find numbers associated with players, scores, distances, or counts.
        </instruction>
        <input>2</input>
        <output>extracted_values</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Determine which values correspond to the specific question being asked. For instance, if the question is about a difference in yards, isolate the longest and shortest touchdown passes.
        </instruction>
        <input>3</input>
        <output>relevant_values</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>
            Perform the required mathematical operation using the relevant values (e.g., subtraction for yard differences).
        </instruction>
        <input>4</input>
        <output>calculation_result</output>
    </node>
    
    <node id="6" type="agent">
        <instruction>
            Verify that the result aligns with the context of the question and ensures no misinterpretation of units or comparisons.
        </instruction>
        <input>5</input>
        <output>final_answer</output>
    </node>
    
    <node id="7" type="output">
        <input>6</input>
    </node>