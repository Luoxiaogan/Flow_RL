# Workflow ID: drop_677_0
# Benchmark: drop
# Data Indices: [3579, 1586, 2333, 3389, 1077]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the problem and identify the key question that needs to be answered.
        </instruction>
        <input>1</input>
        <output>question</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Extract relevant data from the passage that directly answers the question. Focus only on the specific details mentioned in the passage related to the question.
        </instruction>
        <input>1</input>
        <output>relevant_data</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Determine the correct answer by matching the extracted data with the question. Ensure that the answer is unambiguous and directly supported by the passage.
        </instruction>
        <input>2,3</input>
        <output>answer</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>