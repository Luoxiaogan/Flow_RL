# Workflow ID: hotpotqa_583_0
# Benchmark: hotpotqa
# Data Indices: [420, 578, 3229, 2650, 353]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on birth dates and affiliations.</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Verify if the entity matches the query criteria (e.g., Gus Poyet, born in Uruguay, played for Chelsea in Cup Winners' Cup).</prompt>
  </node>
  
  <node id="4" type="agent">
    <prompt>Confirm the exact date of birth from the verified context.</prompt>
  </node>
  
  <node id="5" type="agent">
    <prompt>Validate the result against all provided data to ensure accuracy.</prompt>
  </node>
  
  <node id="6" type="output">
    <prompt>Return the confirmed birth date of Gus Poyet as the final answer.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>