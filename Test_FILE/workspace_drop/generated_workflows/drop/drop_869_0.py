# Workflow ID: drop_869_0
# Benchmark: drop
# Data Indices: [833, 3448, 542, 2588]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key elements in the question and passage that relate to the specific query. Focus on extracting numerical values, names, or events directly relevant to the question.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Process the extracted information step by step to determine the correct answer. If multiple values are present, compare them logically based on the context of the question.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the computed result matches the question's requirements. Ensure no misinterpretation of units, timeframes, or relationships between entities occurred during processing.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>