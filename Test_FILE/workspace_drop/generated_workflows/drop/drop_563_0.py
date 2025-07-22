# Workflow ID: drop_563_0
# Benchmark: drop
# Data Indices: [2401, 3330, 2887, 1055]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Read the problem carefully and identify the key numerical data relevant to the question. Extract all numbers mentioned in the passage that could be related to the answer.</instruction>
        <param name="input">1</param>
        <output>extracted_numbers</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific question being asked. Determine which of the extracted numbers directly answers the question, considering context such as units (e.g., points, field goals, deaths).</instruction>
        <param name="input">2</param>
        <output>relevant_number</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that the relevant number is correctly interpreted in the context of the question. If multiple numbers exist, ensure you are solving for the correct quantity—e.g., difference, total, or ratio—as required by the question.</instruction>
        <param name="input">3</param>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <param name="answer">4</param>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>