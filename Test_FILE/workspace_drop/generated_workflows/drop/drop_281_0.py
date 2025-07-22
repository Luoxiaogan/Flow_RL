# Workflow ID: drop_281_0
# Benchmark: drop
# Data Indices: [961, 3423, 3079, 3146, 3498]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>
      Analyze the problem step by step to identify the key numerical question and relevant data points.
    </instruction>
    <input>problem</input>
    <output>parsed_question, relevant_data</output>
  </node>

  <node id="3" type="agent">
    <instruction>
      Extract the exact values needed to answer the question from the passage. Focus only on numbers directly related to the query.
    </instruction>
    <input>relevant_data</input>
    <output>extracted_values</output>
  </node>

  <node id="4" type="agent">
    <instruction>
      Perform the necessary arithmetic or logical operation using the extracted values to compute the final answer.
    </instruction>
    <input>extracted_values</input>
    <output>computed_answer</output>
  </node>

  <node id="5" type="agent">
    <instruction>
      Verify that the computed answer aligns with the question and that all steps logically follow from the passage.
    </instruction>
    <input>computed_answer, parsed_question</input>
    <output>final_answer</output>
  </node>

  <node id="6" type="output">
    <input>final_answer</input>
  </node>

  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />
  <edge from="5" to="6" />