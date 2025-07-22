# Workflow ID: hotpotqa_321_0
# Benchmark: hotpotqa
# Data Indices: [3027, 1666, 1125, 1204]

<node id="1" type="input">
        <prompt>Understand the problem and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context for each question. Focus on the main subject and associated details.</prompt>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that each extracted piece of information directly answers the question asked. Discard irrelevant data.</prompt>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <prompt>For multi-part questions, ensure all sub-questions are addressed individually before combining results.</prompt>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="agent">
        <prompt>Check consistency: if multiple sources point to the same answer, confirm they align; resolve conflicts logically.</prompt>
        <dependencies>4</dependencies>
    </node>
    <node id="6" type="output">
        <prompt>Return a clear, concise final answer based on verified information. Do not include reasoning or intermediate steps.</prompt>
        <dependencies>5</dependencies>
    </node>