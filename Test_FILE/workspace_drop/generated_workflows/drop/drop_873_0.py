# Workflow ID: drop_873_0
# Benchmark: drop
# Data Indices: [797, 1479, 2260, 785, 3519]

<operator id="0">
    <instruction>Extract key entities and numerical data from the input passage. Focus on numbers, names, and relevant categories that might answer the question.</instruction>
    <input>problem</input>
    <output>entities_and_numbers</output>
  </operator>
  <operator id="1">
    <instruction>Identify the specific question type: count, compare, locate, or calculate. This determines how to process the extracted data.</instruction>
    <input>entities_and_numbers, question</input>
    <output>question_type</output>
  </operator>
  <operator id="2">
    <instruction>Filter and organize relevant data based on the question type. For example, if counting, isolate all items matching the category; if comparing, identify both values.</instruction>
    <input>entities_and_numbers, question_type</input>
    <output>filtered_data</output>
  </operator>
  <operator id="3">
    <instruction>Apply logical reasoning to derive the answer using the filtered data. If multiple steps are needed (e.g., subtraction or comparison), perform them in sequence.</instruction>
    <input>filtered_data, question_type</input>
    <output>answer</output>
  </operator>
  <operator id="4">
    <instruction>Validate the answer by cross-checking against the original passage for accuracy. Ensure no misinterpretation occurred during filtering or reasoning.</instruction>
    <input>answer, problem</input>
    <output>validated_answer</output>
  </operator>