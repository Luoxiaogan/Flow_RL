# Workflow ID: drop_181_0
# Benchmark: drop
# Data Indices: [1515, 1243, 3102, 2267, 2455]

<node id="1" type="input">
        <param name="problem" type="str"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage based on the question. Identify key values and their context.</instruction>
        <param name="input" value="1"/>
        <output name="key_values"/>
    </node>
    
    <node id="3" type="agent">
        <instruction>Perform arithmetic operations or comparisons using the extracted values to answer the specific question step by step.</instruction>
        <param name="input" value="2"/>
        <output name="result"/>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that the result aligns with the question's intent and ensures no misinterpretation of percentages, units, or categories.</instruction>
        <param name="input" value="3"/>
        <output name="final_answer"/>
    </node>
    
    <node id="5" type="output">
        <param name="answer" value="4"/>
    </node>