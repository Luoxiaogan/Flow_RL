# Workflow ID: drop_20_0
# Benchmark: drop
# Data Indices: [3700, 1631, 2774, 2515]

<node id="1">
    <operator>ExtractRelevantInfo</operator>
    <input>problem</input>
    <output>key_info</output>
  </node>
  <node id="2">
    <operator>IdentifyQuestionFocus</operator>
    <input>key_info</input>
    <output>focus_element</output>
  </node>
  <node id="3">
    <operator>LocateValueInPassage</operator>
    <input>focus_element, problem</input>
    <output>raw_answer</output>
  </node>
  <node id="4">
    <operator>ValidateAnswer</operator>
    <input>raw_answer</input>
    <output>final_answer</output>
  </node>
  <node id="5">
    <operator>EnsureConsistency</operator>
    <input>final_answer</input>
    <output>verified_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>