# Workflow ID: hotpotqa_12_0
# Benchmark: hotpotqa
# Data Indices: [3175, 625, 1044, 2727]

<operator id="0">
    <instruction>Think step by step: First, identify the core question and extract relevant context. Then determine the category of the subject (e.g., entertainment type). Finally, verify if the answer fits the category.</instruction>
    <input>problem</input>
    <output>category_guess</output>
  </operator>
  <operator id="1">
    <instruction>Break down the two terms separately. For each term, find its primary use or definition in common knowledge. Compare both to see if they belong to the same category.</instruction>
    <input>category_guess</input>
    <output>term_analysis</output>
  </operator>
  <operator id="2">
    <instruction>Check if either term is widely recognized as a form of entertainment. If so, confirm the specific type (board game, strategy game, etc.). If not, re-evaluate based on known cultural usage.</instruction>
    <input>term_analysis</input>
    <output>entertainment_type</output>
  </operator>
  <operator id="3">
    <instruction>Validate the result by cross-referencing with known examples from similar contexts (e.g., other games, strategies, or media). Ensure consistency across all inputs.</instruction>
    <input>entertainment_type</input>
    <output>final_answer</output>
  </operator>