import openai
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO
import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def extract_text_from_pdf_with_pdfminer(pdf_path="", pdf="",max_tokens=700):
    if pdf_path:
        output_string = StringIO()
        with open(pdf_path, 'rb') as f:
            extract_text_to_fp(f, output_string, laparams=LAParams())
            text = output_string.getvalue()
    elif pdf:
        output_string = StringIO()
        extract_text_to_fp(pdf, output_string, laparams=LAParams())
        text = output_string.getvalue()

    # Split the text to check the token count incrementally
    words = text.split()
    truncated_text = ""
    for word in words:
        if num_tokens_from_string(truncated_text+word,"gpt-3.5-turbo") > max_tokens:
            break
        truncated_text += word + " "
    #print(f"Truncated text: {truncated_text}")
    return truncated_text

def analyze_document(pdf_path):
    pdf_text = extract_text_from_pdf_with_pdfminer(pdf_path)

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond to each question with key-value pairs separated by '#', and use a colon ':' to separate keys and values."},
            {"role": "user", "content": f"Analyze the following document extract: '{pdf_text}'. Provide structured information indicating: is it related to IT/cybersecurity/data privacy/AI?, its subject, the issuer, the country/institution origin, its type (is it a law/norm/regulation/treaty/...),the date of emission, the area of application, the title, two related laws/declarations/norms/regulations if any, and a brief summary (80 tokens max) of the document. Use the format 'is_related:<yes/no>#issuer:<issuer_name>#origin:<origin>#type:<Norm/Law/Regulation/Treaty/...>#subject:<Privacy/Governance/Security/...>#date:<date>#area:<Finance/Healthcare/General/Energy/...>#title:<document_title>#Related_Docs:<doc1><doc2>#abstract:<brief_summary>'."}
        ],
        temperature=0.4,
        max_tokens=280,
        top_p=1
    )
    return response.choices[0].message.content

# def analyze_document(pdf_path):
#     pdf_text = extract_text_from_pdf_with_pdfminer(pdf_path)

#     client = openai.OpenAI()
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo-1106",
#         response_format={"type": "json_object"},
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant designed to output structured data in JSON format."},
#             {"role": "user", "content": f"Analyze the following document extract: '{pdf_text}'. Provide structured information in JSON format indicating: is it related to IT/cybersecurity/data privacy/AI (is_related), its subject (subject), the issuer (issuer), the country/institution origin (origin), its type (type), the date of emission (date), the area of application (area_of_application), the title (name), two related laws/declarations/norms/regulations (related_docs), and a brief summary [80 tokens max] (abstract) of the document."}
#         ],
#         temperature=0.4,
#         max_tokens=250,
#         top_p=1
#     )

#     return response.choices[0].message.content

def regenerate_document_field(pdf, field, temperature):
    pdf_text = extract_text_from_pdf_with_pdfminer(pdf=pdf)
    print(f"field: {field}, temperature: {temperature}")
    client = openai.OpenAI()
    
    # Determine the content of the GPT request based on the field
    if field == 'title':
        user_content = f"What is the the title of the following document extract: '{pdf_text}'. Plese answer in the format 'title:<document_title>'."
    elif field == 'date':
        user_content = f"What is the date of emission for the following document extract: '{pdf_text}'. Plese answer in the format 'date:<date>'."
    elif field == 'abstract':
        user_content = f"Make an abstract (80 tokens max) based on the following document extract: '{pdf_text}'. Plese answer in the format 'abstract:<brief_summary>'."
    elif field == 'related_docs':
        user_content =  f"List two titles (just the titles) of documents related to this extract, excluding the document's extract title itself (example: document from where the extract was taken has the title A. You cant answer Related_Docs:<A>,<B> or <A, long version of the title>, <B>): '{pdf_text}'. Respond 'related_docs:<related_doc1_title>,<related_doc2_title>' or 'related_docs:None' if none."
    elif field == 'issuer':
        user_content = f"What is the issuer of the following document extract: '{pdf_text}'. Plese answer in the format 'issuer:<issuer_name>'."
    elif field == 'origin':
        user_content = f"What is the country/institution origin of the following document extract: '{pdf_text}'. Plese answer in the format 'origin:<origin>'."
    elif field == 'type':
        user_content = f"What is the type (law/norm/regulation/treaty/...) of the following document extract: '{pdf_text}'. Plese answer in the format 'type:<type>'."
    elif field == 'subject':
        user_content = f"What is the subject (privacy/governance/cybersecurity/...) of the following document extract: '{pdf_text}'. Plese answer in the format 'subject:<subject>'."
    elif field == 'area':
        user_content = f"What is the area of application (finance/healthcare/general/energy/...) of the following document extract: '{pdf_text}'. Plese answer in the format 'area:<area>'."
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Please reponde in the format 'field:<field_value>'."},
            {"role": "user", "content": user_content}
        ],
        temperature=temperature,
        max_tokens=100,
        top_p=1
    )
    return response.choices[0].message.content
