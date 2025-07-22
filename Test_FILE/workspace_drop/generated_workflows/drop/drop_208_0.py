# Workflow ID: drop_208_0
# Benchmark: drop
# Data Indices: [417, 2070, 2412, 323]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical values and relationships in the passage. Focus on extracting relevant data points that directly answer the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Perform arithmetic or logical operations based on extracted values. If the question involves comparison, compute the difference or ratio. If it's a direct value, return it.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the result against the context to ensure accuracy and relevance. Ensure no misinterpretation of percentages or units occurs.</instruction>
    </node>
    <node id="5" type="output">
        <description>Return the final answer based on verified computation.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>