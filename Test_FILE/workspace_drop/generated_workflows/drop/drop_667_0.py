# Workflow ID: drop_667_0
# Benchmark: drop
# Data Indices: [1702, 3284, 207, 2634, 27]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key event or detail in the passage that directly answers the question. Break down the passage into chronological or logical segments to locate relevant information.</instruction>
    <input>1</input>
    <output>key_event</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract numerical or categorical data from the key event, such as scores, team names, or time-specific actions, to match the question's requirement.</instruction>
    <input>2</input>
    <output>extracted_data</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the extracted data logically aligns with the question and is not contradicted by other parts of the passage. If conflicting, resolve by checking context.</instruction>
    <input>3</input>
    <output>validated_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>