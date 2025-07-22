# Workflow ID: hotpotqa_522_0
# Benchmark: hotpotqa
# Data Indices: [516, 945, 3353, 3888]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the problem. Break down the question into its core components and determine what information is needed to solve it.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Extract relevant data from the context that directly answers the question. Focus on specific facts, dates, or attributes related to the entities mentioned.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Compare the extracted information to determine which entity (Kasetsart or Bilkent) offers a broader academic scope based on the number and diversity of disciplines listed.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Validate the conclusion by cross-referencing the breadth of academic programs at both universities using the provided context. Ensure no critical detail is overlooked.</instruction>
    </node>
    <node id="6" type="output">
        <description>Return the university with the wider variety of academic disciplines based on evidence from the context.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>