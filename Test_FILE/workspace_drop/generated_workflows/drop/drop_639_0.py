# Workflow ID: drop_639_0
# Benchmark: drop
# Data Indices: [1059, 3331, 2726, 816]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key elements in the passage relevant to the question. Think step by step: first, determine what is being asked; second, locate all numerical or descriptive data that relates directly to the query; third, extract only the necessary information without adding assumptions.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Process the extracted data to answer the specific question. For each piece of data, evaluate whether it meets the criteria of the question (e.g., longest, shortest, total points). If multiple candidates exist, compare them logically to find the correct one.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Validate the result by cross-checking with the original passage. Ensure no misinterpretation occurred—especially for ambiguous terms like "shortest" or "longest"—and confirm the answer aligns with the context of the passage.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <description>Return the final answer based on validated processing.</description>
        <depends_on>4</depends_on>
    </node>