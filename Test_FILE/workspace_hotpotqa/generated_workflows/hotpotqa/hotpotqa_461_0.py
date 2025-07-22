# Workflow ID: hotpotqa_461_0
# Benchmark: hotpotqa
# Data Indices: [3650, 3248, 1601, 2227]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context for the first question. Focus on the creator of the "Survivor" franchise.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Extract relevant information from context for the second question. Identify the country where both Gleaston Castle and Ulverston are located.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Extract relevant information from context for the third question. Determine if "La Périchole" and "Mignon" are by the same composer.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Extract relevant information from context for the fourth question. Find the size in acres of the district in Selma where shotgun houses are found.</prompt>
  </node>
  <node id="6" type="agent">
    <prompt>Combine all extracted answers into a single structured response.</prompt>
  </node>
  <node id="7" type="output">
    <prompt>Return the final answer based on all agents' outputs.</prompt>
  </node>

  <!-- Edges -->
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="1" to="4"/>
  <edge from="1" to="5"/>
  <edge from="2" to="6"/>
  <edge from="3" to="6"/>
  <edge from="4" to="6"/>
  <edge from="5" to="6"/>
  <edge from="6" to="7"/>