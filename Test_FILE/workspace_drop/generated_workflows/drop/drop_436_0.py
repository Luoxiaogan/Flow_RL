# Workflow ID: drop_436_0
# Benchmark: drop
# Data Indices: [1620, 3714, 2665, 1372]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key numerical data points in the passage relevant to the question. Break down the problem step by step.</instruction>
    <input>1</input>
    <output>key_data_points</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Extract and organize all values that meet the condition specified in the question (e.g., distances for touchdowns, percentages for demographics).</instruction>
    <input>2</input>
    <output>filtered_values</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Apply mathematical operations or logical comparisons to derive the final answer based on the filtered values.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Validate the result by cross-checking with original passage data to ensure accuracy.</instruction>
    <input>4</input>
    <output>validated_result</output>
  </node>
  
  <node id="6" type="output">
    <input>5</input>
    <parameter>answer</parameter>
  </node>