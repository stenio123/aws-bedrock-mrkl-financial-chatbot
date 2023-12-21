
from utils.llm_wrapper import get_llm
from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate

from utils.aws_services import get_kendra_client, get_kendra_index

_DEFAULT_TEMPLATE = """
Human:    
Answer the following question to the best of your ability based on the context provided.
Provide an answer and provide sources and the source link to where the relevant information can be found. Include this at the end of the response
Do not include information that is not relevant to the question.
Only provide information based on the context provided, and do not make assumptions
Only Provide the source if relevant information came from that source in your answer
Only provide the source if the link actually exists and was returned in the response, do not create or suggest links


Question: {question}

Context: {context}


Assistant:

"""

PROMPT = PromptTemplate(
    input_variables=["question", "context"], template=_DEFAULT_TEMPLATE
)




def get_rag_chain_response(question, context):
    combined_input = {
        "question": question,
        "context": context
    }
    llm = get_llm()

    rag_chain = LLMChain(
        llm=llm,
        verbose=True, 
        prompt=PROMPT, 
    )
    output = rag_chain.run(combined_input)
    #print(output)
    return(output)

def run_rag_search(question):
    """
    Primary function that performs a kendra search, using the retrieve API and passes the kendra response into the
    invoke LLM function.
    :param question: The question the user inputs within app.py or the frontend
    :return: Returns the final response of the LLM that was created by the invokeLLM function
    """
    # initiating kendra client
    kendra_instance = get_kendra_client()
    index = get_kendra_index()
    # performing the retrieve call against Kendra
    kendra_response = kendra_instance.retrieve(
        IndexId=index,
        QueryText=question,
        PageNumber=1,
        PageSize=15
    )
    # passing in the original question, and various kendra responses as context into the LLM
    return get_rag_chain_response(question, kendra_response)

#response = run_rag_search(" What are the main topics from Amazon investor call?")
#print(response)