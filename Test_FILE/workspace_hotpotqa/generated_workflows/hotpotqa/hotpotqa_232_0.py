# Workflow ID: hotpotqa_232_0
# Benchmark: hotpotqa
# Data Indices: [83, 2522, 2528, 523, 601]

<operator id="0" type="agent">
        <instruction>Identify the key elements in the question and determine which agent should process each part.</instruction>
    </operator>
    <operator id="1" type="agent">
        <instruction>Extract the relevant information from the context related to the question's subject.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Verify if the extracted information directly answers the question or needs further processing.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Combine insights from previous operators to form a coherent response.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Validate the final answer against all available context to ensure accuracy.</instruction>
    </operator>
    <operator id="5" type="agent">
        <instruction>Format the final output according to the required structure without including problem-specific details.</instruction>
    </operator>