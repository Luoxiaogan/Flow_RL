# Workflow ID: drop_460_0
# Benchmark: drop
# Data Indices: [460, 3283, 2881, 527]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data relevant to the question in the passage. Focus on the specific statistic being asked for, such as passes, yards, troops, or penalties.</instruction>
    <input>1</input>
    <output>key_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract the exact value from the passage that answers the question. If multiple values are present, determine which one matches the context of the question (e.g., total passes for Brees, not just completions).</instruction>
    <input>2</input>
    <output>extracted_value</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the extracted value is correct and directly answers the question. Cross-check with any related details in the passage to avoid misinterpretation (e.g., distinguishing between attempts and completions).</instruction>
    <input>3</input>
    <output>verified_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>