# Workflow ID: drop_542_0
# Benchmark: drop
# Data Indices: [3572, 2653, 760, 186, 619]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the problem statement to identify the key question and relevant data points. Break down the task into clear steps.
        </instruction>
        <input>1</input>
        <output>step_by_step_analysis</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Extract numerical values or counts directly related to the question from the passage. Focus only on the relevant information for the query.
        </instruction>
        <input>2</input>
        <output>extracted_data</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Determine how the extracted data answers the specific question. If multiple items contribute, sum them appropriately.
        </instruction>
        <input>3</input>
        <output>computed_answer</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>
            Validate the computed answer by cross-referencing with the passage again. Ensure no misinterpretation occurred.
        </instruction>
        <input>4</input>
        <output>validated_answer</output>
    </node>
    
    <node id="6" type="output">
        <input>5</input>
        <output>final_answer</output>
    </node>