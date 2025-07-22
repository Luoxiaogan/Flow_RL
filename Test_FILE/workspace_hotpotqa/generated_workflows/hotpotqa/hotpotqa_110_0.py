# Workflow ID: hotpotqa_110_0
# Benchmark: hotpotqa
# Data Indices: [3910, 1144, 2742, 2105]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the relevant context for each question. Focus on specific details like names, dates, and categories.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>For each question, isolate the answer by matching the correct entity from the context. Avoid overgeneralization or mixing unrelated data.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>Verify that the extracted answer matches the exact requirement of the question—e.g., ethnicity, ideology, album title, etc.</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on validated extraction. Ensure clarity and precision without additional explanation.</prompt>
        <depends_on>4</depends_on>
    </node>