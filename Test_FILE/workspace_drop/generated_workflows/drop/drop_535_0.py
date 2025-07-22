# Workflow ID: drop_535_0
# Benchmark: drop
# Data Indices: [962, 1971, 1986, 472, 213]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify the key numerical information relevant to the question.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract all numeric values related to the question from the passage. For example, if the question asks about touchdowns, find all yardage figures associated with touchdowns.</prompt>
  </node>
  <node id="3" type="filter">
    <prompt>Filter out only the values that directly answer the question—ignore unrelated numbers.</prompt>
  </node>
  <node id="4" type="compare">
    <prompt>Compare the filtered values to determine the smallest (or largest, depending on the question).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the comparison result.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>