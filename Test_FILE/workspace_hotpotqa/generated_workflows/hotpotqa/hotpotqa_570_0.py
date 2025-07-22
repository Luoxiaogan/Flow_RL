# Workflow ID: hotpotqa_570_0
# Benchmark: hotpotqa
# Data Indices: [2839, 2918, 1475, 3213]

<node id="1" type="input">
        <prompt>Understand the task and identify key entities in the question.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the question. Focus on direct matches or clear associations.</prompt>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information against known facts or cross-reference with other entries in the context for consistency.</prompt>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <prompt>Determine the correct answer by resolving any ambiguity or conflict between sources.</prompt>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the validated reasoning.</prompt>
        <dependencies>4</dependencies>
    </node>