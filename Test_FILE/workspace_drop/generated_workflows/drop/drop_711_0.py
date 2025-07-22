# Workflow ID: drop_711_0
# Benchmark: drop
# Data Indices: [2023, 1593, 832, 3351, 105]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="process">
        <operator>analyze_question</operator>
        <input>1</input>
        <output>2</output>
    </node>
    
    <node id="3" type="process">
        <operator>extract_relevant_data</operator>
        <input>2</input>
        <output>3</output>
    </node>
    
    <node id="4" type="process">
        <operator>calculate_result</operator>
        <input>3</input>
        <output>4</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>