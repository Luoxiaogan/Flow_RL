# Workflow ID: drop_806_0
# Benchmark: drop
# Data Indices: [2283, 1078, 3580, 3675, 945]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key numerical data points relevant to the question. Extract all values that can be compared or calculated.</instruction>
    <input>1</input>
    <output>extracted_values</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>For each value, determine its role in answering the question—e.g., numerator, denominator, or comparison point.</instruction>
    <input>2</input>
    <output>role_analysis</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Apply mathematical operations (e.g., subtraction, division) based on the roles identified to compute the required result.</instruction>
    <input>3</input>
    <output>calculation_result</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Validate the result by checking against the original passage for consistency and correctness.</instruction>
    <input>4</input>
    <output>validation</output>
  </node>
  
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>