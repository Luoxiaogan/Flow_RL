# Workflow ID: drop_501_0
# Benchmark: drop
# Data Indices: [1797, 745, 1333, 1187]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that answers the question. Identify all numbers mentioned in relation to the query, focusing on quantities, dates, or measurements directly tied to the answer.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify which number(s) in the extracted data directly correspond to the quantity asked in the question. If multiple values exist, determine which one is most relevant based on context (e.g., shortest field goal implies the minimum value among all field goals).</instruction>
        <input>2</input>
        <output>relevant_value</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that the relevant value is indeed the correct answer by cross-checking with the original passage's context—ensure it matches both the metric (e.g., yards) and the condition (e.g., shortest).</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
    </node>