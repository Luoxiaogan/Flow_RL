# Workflow ID: drop_478_0
# Benchmark: drop
# Data Indices: [2015, 1803, 1192, 3051, 3627]

<node id="1" type="input">
    <param name="problem" type="string"/>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    <param name="question" type="string"/>
    <param name="passage" type="string"/>
    <output>numerical_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Identify and isolate the components mentioned in the question (e.g., touchdowns, runs, families).</instruction>
    <param name="numerical_data" type="list"/>
    <param name="question" type="string"/>
    <output>components</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Calculate the required comparison or percentage based on the identified components.</instruction>
    <param name="components" type="dict"/>
    <param name="question" type="string"/>
    <output>result</output>
  </node>
  
  <node id="5" type="output">
    <param name="final_answer" type="any"/>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>