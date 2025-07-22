# Workflow ID: drop_562_0
# Benchmark: drop
# Data Indices: [3070, 680, 44, 1199]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical question in the passage and locate the relevant data.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract the specific value or values needed to answer the question, focusing on percentages, counts, or time spans as appropriate.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform any necessary arithmetic (addition, subtraction, multiplication, division) to compute the final answer based on the extracted data.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that the computed answer matches the question's requirement (e.g., percentage, count, duration).</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>