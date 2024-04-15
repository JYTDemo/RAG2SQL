import chromadb
import sqlite3
from langchain_community.embeddings import HuggingFaceEmbeddings
import pandas as pd
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
from dotenv import load_dotenv
from langchain_community.chat_models import AzureChatOpenAI

class datachat():
    def __init__(self):
        load_dotenv()
        client = chromadb.Client()
        self.collection = client.get_or_create_collection(name="ddl_collection", metadata={"hnsw:space":"cosine"})
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    def exe_sql(self,statement):
        conn = sqlite3.connect('./db/HR.db')
        df = pd.read_sql_query(statement, conn)
        conn.close()
        return df


    def get_meta(self, query):
        query_v = self.embeddings.embed_query(query)
        select_meta =self.collection.query(query_embeddings=query_v,n_results = 8)
        return (select_meta)


    def extract_code(self,response):
        start = 0
        q = ""
        temp_block=""
        for line in response.splitlines(): 
            if '```sql' in line and start==0:
                start=1
            if '```' == line.strip() and start==1:
                start =0
                break
            if start ==1 and '```' not in line:
                q=q+'\n'+line

        return q


        
    def vectorize(self):
        statement = '''select sql from sqlite_master where type = 'table' ;'''
        df = self.exe_sql(statement)
        meta = df.to_dict(orient='records')

        documents_list = []
        embeddings_list = []
        ids_list = []

        for i, chunk in enumerate(meta):
            vector = self.embeddings.embed_query(str(chunk))
            
            documents_list.append(str(chunk))
            embeddings_list.append(vector)
            ids_list.append(f"ddl_{i}")

        self.collection.add(
            embeddings=embeddings_list,
            documents=documents_list,
            ids=ids_list
        )
        return


    def data_ops(self,query):   
        llm = AzureChatOpenAI(deployment_name=os.getenv('DEPLOYEMENT_NAME'),
                            temperature=0.00,
                            max_tokens=4000,
                            callbacks=[StreamingStdOutCallbackHandler()]
                            )


        instruction = """
        As a SQL developer generate SQL statement for the query with reference to the database objects in the database schema.

        Database schema:
        {meta}

        question: {input}

        answer:

        """

        #query = "what is the location of the employee Steven "
        select_meta=self.get_meta(query)
        prompt_template = PromptTemplate.from_template(instruction)
        agent = LLMChain(llm=llm,prompt=prompt_template)
        response = agent.invoke({"input":query,"meta":select_meta})

        gen_sql = self.extract_code(response['text'])
        print(gen_sql)
        df = self.exe_sql(gen_sql)
        return df
