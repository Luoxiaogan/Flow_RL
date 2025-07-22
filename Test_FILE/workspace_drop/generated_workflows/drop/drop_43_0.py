# Workflow ID: drop_43_0
# Benchmark: drop
# Data Indices: [2971, 2484, 3965, 2594]

<node id="1" type="input">
    <param name="problem" type="str"/>
  </node>
  
  <node id="2" type="agent">
    <instruction>
      Think step by step: First, identify the key elements in the question. Then, locate the relevant information in the passage. Finally, extract or calculate the answer based on that information.
    </instruction>
    <input>problem</input>
    <output>answer</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>
      Analyze the passage for numerical data related to the question. If the question asks for a count, sum, average, or percentage, ensure you compute it correctly using the values found in the text.
    </instruction>
    <input>problem</input>
    <output>raw_data</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>
      Verify that the extracted data from the passage directly answers the question. If not, re-evaluate the passage for any missing or misinterpreted details. Ensure no irrelevant information is included in the final answer.
    </instruction>
    <input>raw_data</input>
    <output>validated_answer</output>
  </node>
  
  <node id="5" type="output">
    <input>validated_answer</input>
    <output>final_answer</output>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="3" to="4"/>
  <edge from="2" to="4"/>
  <edge from="4" to="5"/>