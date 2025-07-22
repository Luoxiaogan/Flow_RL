# Workflow ID: hotpotqa_172_0
# Benchmark: hotpotqa
# Data Indices: [1623, 2242, 780, 293, 3674]

<node id="1" type="input">
    <prompt>Understand the question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the subject and their profession. Focus on the person born on October 23, 1966, who is an Italian professional racing driver and paracyclist.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Find which car company this person races for. Look for explicit mentions of team affiliations or sponsorships in the context.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the connection between the person and the car company using contextual evidence (e.g., race results, team logos, or statements).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the car company name that matches the racing driver's current or most notable affiliation.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>