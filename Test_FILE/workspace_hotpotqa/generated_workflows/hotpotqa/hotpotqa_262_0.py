# Workflow ID: hotpotqa_262_0
# Benchmark: hotpotqa
# Data Indices: [2996, 3207, 719, 3042]

<node id="1" type="input">
        <prompt>Process the given problem context to identify key entities and relationships.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context that directly answers the question. Focus on precise details like names, dates, or roles.</prompt>
        <dependencies>1</dependencies>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information against all provided context to ensure accuracy and avoid contradictions.</prompt>
        <dependencies>2</dependencies>
    </node>
    <node id="4" type="agent">
        <prompt>Structure the verified answer in a clear, concise format suitable for direct output.</prompt>
        <dependencies>3</dependencies>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the structured information from node 4.</prompt>
        <dependencies>4</dependencies>
    </node>