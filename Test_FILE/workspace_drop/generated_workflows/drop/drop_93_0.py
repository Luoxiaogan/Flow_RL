# Workflow ID: drop_93_0
# Benchmark: drop
# Data Indices: [2900, 1039, 2073, 804]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical or categorical data from the passage that answers the question. Focus on precise values and their context.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations (e.g., percentages, differences, rankings) based on extracted data to derive the answer step by step.</instruction>
    <input>2</input>
    <output>calculated_answer</output>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the calculated answer against the original passage for consistency and accuracy. If inconsistent, recheck logic or data extraction.</instruction>
    <input>3</input>
    <output>validated_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>