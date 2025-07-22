# Workflow ID: drop_558_0
# Benchmark: drop
# Data Indices: [1780, 3784, 1904, 3629, 2610]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Think step by step: First, identify the key information in the passage that relates to the question. Then, extract the relevant numbers or facts. Finally, perform the necessary calculation or comparison to determine the answer.
        </instruction>
        <input>problem</input>
        <output>step_by_step_analysis</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Based on the step-by-step analysis, determine the final answer to the question. Ensure that your reasoning is clear and directly tied to the extracted data from the passage.
        </instruction>
        <input>step_by_step_analysis</input>
        <output>final_answer</output>
    </node>
    
    <node id="4" type="output">
        <param name="answer" type="string"/>
        <input>final_answer</input>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>