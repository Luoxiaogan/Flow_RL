# Workflow ID: drop_777_0
# Benchmark: drop
# Data Indices: [2938, 153, 2032, 3639, 98]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question. Identify all values that could be answers.</instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>For each extracted value, determine if it answers the specific question. If yes, store it as a candidate answer.</instruction>
        <input>2</input>
        <output>candidates</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Among the candidates, identify the correct one by verifying against the context of the question. Discard any irrelevant or incorrect values.</instruction>
        <input>3</input>
        <output>correct_answer</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Validate the correct answer by cross-checking with the original passage to ensure no misinterpretation occurred.</instruction>
        <input>4</input>
        <output>validated_answer</output>
    </node>
    
    <node id="6" type="output">
        <input>5</input>
        <output>final_answer</output>
    </node>