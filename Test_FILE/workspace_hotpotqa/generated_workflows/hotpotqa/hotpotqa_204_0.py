# Workflow ID: hotpotqa_204_0
# Benchmark: hotpotqa
# Data Indices: [502, 680, 1643, 1197]

<operator id="0">
        <instruction>Identify the common job between Danny Worsnop and Mina Caputo by analyzing their professional roles in music.</instruction>
        <input>Context about Danny Worsnop and Mina Caputo</input>
        <output>Lead singer</output>
    </operator>
    <operator id="1">
        <instruction>Verify that both individuals are primarily recognized for their vocal performances in rock/metal bands.</instruction>
        <input>Context on Danny Worsnop's band Asking Alexandria and Mina Caputo's band Life of Agony</input>
        <output>Confirmed as lead singers</output>
    </operator>
    <operator id="2">
        <instruction>Check if either has held other primary roles (e.g., songwriter, guitarist) that might overshadow their singing role.</instruction>
        <input>Information on Danny Worsnop’s songwriting contributions and Mina Caputo’s role as a founding member</input>
        <output>Singing remains the core shared role</output>
    </operator>
    <operator id="3">
        <instruction>Confirm that the term "lead singer" is consistent across both artists’ biographies and collaborations.</instruction>
        <input>References to guest vocals, band roles, and public recognition</input>
        <output>Consistent identification as lead singers</output>
    </operator>
    <operator id="4">
        <instruction>Aggregate findings from all operators to determine the final answer.</instruction>
        <input>Outputs from operators 0–3</input>
        <output>Lead singer</output>
    </operator>
    <connection>
        <from>0</from>
        <to>4</to>
    </connection>
    <connection>
        <from>1</from>
        <to>4</to>
    </connection>
    <connection>
        <from>2</from>
        <to>4</to>
    </connection>
    <connection>
        <from>3</from>
        <to>4</to>
    </connection>