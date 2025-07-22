# Workflow ID: hotpotqa_254_0
# Benchmark: hotpotqa
# Data Indices: [1137, 2234, 2864, 1610]

<node id="1" type="input">
        <prompt>Understand the task and identify key elements from the problem context.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Step 1: Analyze the question and extract relevant keywords or entities. Step 2: Search the context for direct matches or related information. Step 3: Determine if the answer is explicitly stated or requires inference.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Step 1: If the answer is not directly found, look for indirect clues in the context. Step 2: Use logical reasoning to connect known facts (e.g., nationality, profession, associations). Step 3: Eliminate incorrect options based on evidence.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Step 1: Cross-validate findings across multiple context snippets. Step 2: Confirm consistency with external knowledge where applicable. Step 3: Resolve any contradictions or ambiguities by prioritizing the most specific or recent information.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on synthesized results from all agents. Ensure clarity and correctness.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>