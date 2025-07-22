# Workflow ID: hotpotqa_88_0
# Benchmark: hotpotqa
# Data Indices: [3940, 584, 1560, 2160]

<node id="1" type="input">
    <prompt>Understand the task and identify key elements in the problem.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the context that directly answers the question. Focus on frequency of publication for magazines, hosts of shows, locations of buildings, or creators of TV series.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted data to determine which option satisfies the condition in the question (e.g., more frequent publication, correct host, river at mouth, creator of show).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the correctness of your comparison by cross-referencing with other context details to avoid misinterpretation.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer based on verified data, ensuring it directly addresses the question without additional explanation.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>