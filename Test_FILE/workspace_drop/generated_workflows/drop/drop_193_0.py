# Workflow ID: drop_193_0
# Benchmark: drop
# Data Indices: [3391, 1528, 3114, 607]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the relevant information in the passage that answers the question. Focus on the specific details mentioned about the event or value being asked.</instruction>
        <input>1</input>
        <output>retrieved_info</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Extract the exact numerical value or event from the retrieved information. If multiple values exist, determine which one is directly relevant to the question.</instruction>
        <input>2</input>
        <output>extracted_value</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that the extracted value matches the question's requirement — for example, if the question asks for a shortest field goal, ensure you're not selecting the longest or any other metric.</instruction>
        <input>3</input>
        <output>validated_answer</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>