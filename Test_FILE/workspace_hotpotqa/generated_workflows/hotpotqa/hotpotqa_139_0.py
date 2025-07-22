# Workflow ID: hotpotqa_139_0
# Benchmark: hotpotqa
# Data Indices: [2451, 2889, 1038, 1771, 2173]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context for each entity mentioned in the question.</prompt>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further processing.</prompt>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <prompt>Apply logical reasoning to connect the verified information into a coherent answer.</prompt>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the reasoning from node 4.</prompt>
        <dependencies>4</dependencies>
    </node>