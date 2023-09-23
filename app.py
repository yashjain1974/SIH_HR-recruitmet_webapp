from flask import Flask, render_template, request, session, redirect, url_for
from azure.storage.blob import BlobServiceClient
from io import StringIO,BytesIO
from flask_cors import CORS
import os
import fitz
app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    resume_text = ""
    pdf_document = fitz.open(pdf_path)
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        resume_text += page.get_text("text")
    pdf_document.close()
    return resume_text


@app.route('/')
def index():
    return render_template('main.html')
@app.route('/analyze_cv')
def analyseCv():
    return render_template('analyzeCV.html')
@app.route('/analyze_job')
def analyseJob():
    return render_template('analyzeJob.html')
@app.route('/analyze_job', methods=['POST'])
def upload_job():
    if request.method == 'POST':
        if 'file' in request.files:  # User chose the file upload option
            file = request.files['file']
            filenames=""
            if file:
                try:
                    container_client.upload_blob(f"{file.filename}", file,overwrite=True) # upload the file to the container using the filename as the blob name
                    filenames += file.filename + "<br /> "
                except Exception as e:
                    print(e)
                    print("Ignoring duplicate filenames") # ignore duplicate filenames
                blob_client = container_client.get_blob_client(file.filename) # get blob client to interact with the blob and get blob url
                with BytesIO() as input_blob:
                    blob_client.download_blob().download_to_stream(input_blob)
                    input_blob.seek(0)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(input_blob.read())
                        temp_file_path = temp_file.name
                    resume_text = extract_text_from_pdf(temp_file_path)
                    os.remove(temp_file_path)
            
                template = """
                For the following job description pdf, extract the following: company name, job description, company description, 
                job requirements. Start each group following this pattern: [<GROUP NAME>], e.g. for 'Skills' do '[SKILLS]'. 
                Return the information as detailed as possible
    

                {chat_history}
                {human_input}"""
            
                prompt = PromptTemplate(
                    input_variables=["chat_history", "human_input"],
                    template=template
                )

                memory = ConversationBufferMemory(memory_key="chat_history")

                llm_chain = LLMChain(
                    llm=OpenAIChat(model="gpt-3.5-turbo"),
                    prompt=prompt,
                    verbose=True,
                    memory=memory,
                )

                res = llm_chain.predict(human_input=resume_text)
                print(res)
                return render_template('analyzeJob.html', parsed_resume=res, error=None)
            else:
                return render_template('analyzeJob.html', parsed_resume=None, error='Error uploading file. Only PDFs are allowed.')
        elif 'job_description' in request.form:  # User chose the textarea option
            job_description = request.form['job_description']
            template = """
                For the following job description text, extract the following: company name, job description, company description, 
                job requirements. Start each group following this pattern: [<GROUP NAME>], e.g. for 'Skills' do '[SKILLS]'. 
                Return the information as detailed as possible
    

                {chat_history}
                {human_input}"""
            
            prompt = PromptTemplate(
                    input_variables=["chat_history", "human_input"],
                    template=template
                )

            memory = ConversationBufferMemory(memory_key="chat_history")

            llm_chain = LLMChain(
                    llm=OpenAIChat(model="gpt-3.5-turbo"),
                    prompt=prompt,
                    verbose=True,
                    memory=memory,
                )

            res = llm_chain.predict(human_input=job_description)

            return render_template('analyzeJob.html', parsed_resume=res, error=None)
    return render_template('analyzeJob.html', parsed_resume=None, error='Error uploading file.')

@app.route('/analyze_cv', methods=['POST'])
def upload_cv():
    if request.method == 'POST':
        file = request.files['file']
        filenames=""
        if file:
            try:
                container_client.upload_blob(f"{file.filename}", file,overwrite=True) # upload the file to the container using the filename as the blob name
                filenames += file.filename + "<br /> "
            except Exception as e:
                print(e)
                print("Ignoring duplicate filenames") # ignore duplicate filenames
            blob_client = container_client.get_blob_client(file.filename) # get blob client to interact with the blob and get blob url
            with BytesIO() as input_blob:
                blob_client.download_blob().download_to_stream(input_blob)
                input_blob.seek(0)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(input_blob.read())
                    temp_file_path = temp_file.name
                resume_text = extract_text_from_pdf(temp_file_path)
                os.remove(temp_file_path)

            res = llm_chain.predict(human_input=resume_text)
            print(res)
            return render_template('analyzeCV.html', parsed_resume=res, error=None)
        else:
            return render_template('analyzeCV.html', parsed_resume=None, error='Error uploading file. Only PDFs are allowed.')
    return render_template('analyzeCV.html', parsed_resume=None, error='Error uploading file.')
@app.route('/analyze_job', methods=['POST'])
def upload_job():
    if request.method == 'POST':
        if 'file' in request.files:  # User chose the file upload option
            file = request.files['file']
            filenames=""
            if file:
                try:
                    container_client.upload_blob(f"{file.filename}", file,overwrite=True) # upload the file to the container using the filename as the blob name
                    filenames += file.filename + "<br /> "
                except Exception as e:
                    print(e)
                    print("Ignoring duplicate filenames") # ignore duplicate filenames
                blob_client = container_client.get_blob_client(file.filename) # get blob client to interact with the blob and get blob url
                with BytesIO() as input_blob:
                    blob_client.download_blob().download_to_stream(input_blob)
                    input_blob.seek(0)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(input_blob.read())
                        temp_file_path = temp_file.name
                    resume_text = extract_text_from_pdf(temp_file_path)
                    os.remove(temp_file_path)
            


            return render_template('analyzeJob.html', parsed_resume=res, error=None)
    return render_template('analyzeJob.html', parsed_resume=None, error='Error uploading file.')
if __name__ == "__main__":
    app.run(debug=True)
