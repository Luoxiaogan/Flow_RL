# Workflow ID: hotpotqa_502_0
# Benchmark: hotpotqa
# Data Indices: [3349, 2648, 3022, 2236]

<operator id="0">
    <instruction>Think step by step: First, identify the key elements in the question and determine what needs to be compared or verified.</instruction>
    <input>problem</input>
    <output>step1_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Next, extract relevant facts from the context that directly address the comparison in the question.</instruction>
    <input>step1_analysis</input>
    <output>step2_extraction</output>
  </operator>
  <operator id="2">
    <instruction>Now, compare the extracted facts logically to determine if the statement in the question is true or false.</instruction>
    <input>step2_extraction</input>
    <output>step3_comparison</output>
  </operator>
  <operator id="3">
    <instruction>Finally, synthesize your findings into a clear and concise answer that directly responds to the original question.</instruction>
    <input>step3_comparison</input>
    <output>final_answer</output>
  </operator>