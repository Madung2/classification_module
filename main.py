import streamlit as st
from PIL import Image
from encoding import image_to_base64
import requests
from dotenv import load_dotenv
import json
import time
import os
import io
import base64
import shutil
from queue import Queue
load_dotenv()
domainId = os.getenv('domainId')
templateId = os.getenv('templateId')
saved_dir = os.getenv('saved_dir')

##################################function########################################


def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def delete_saved_dir():
    documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
    saved_path = os.path.join(documents_dir, saved_dir)
    if os.path.exists(saved_path):
        shutil.rmtree(saved_path)
        st.success(f"{saved_path} 디렉토리를 삭제했습니다.")

def list_files_in_directory(directory):
    file_structure = {}
    for root, dirs, files in os.walk(directory):
        relative_path = os.path.relpath(root, directory)
        file_structure[relative_path] = files
    return file_structure

def display_files(directory):
    file_structure = list_files_in_directory(directory)
    print('####################################')
    print(file_structure)
    print('####################################')
    for folder, files in file_structure.items():

        if len(files) != 0:
            st.markdown("***")
            st.write(f"**📁{folder}**")
        for file in files:
            file_path = os.path.join(directory, folder, file)
            with open(file_path, "rb") as file_data:
                if st.download_button(
                    label=f"📄{file}",
                    data=file_data,
                    file_name=file,
                    key=file_path
                ):
                    st.session_state.selected_image_path = file_path

##################################streamlit#####################################
# 페이지 제목
st.title("Image Classifier")



st.markdown("""
    <style>
    .big-button {
        display: block;
        width: 100%;
        height: 60px;
        font-size: 20px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)
# 사이드바에 초기화 버튼 추가
with st.sidebar:
    if st.button("파일 업로드 초기화", key="delete_button"):
        delete_saved_dir()
    documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
    saved_path = os.path.join(documents_dir, saved_dir)
    if os.path.exists(saved_path):
        #st.write(f"{saved_path}")
        display_files(saved_path)


# 선택한 이미지를 메인 화면에 표시
if "selected_image_path" in st.session_state:
    image_path = st.session_state.selected_image_path
    image = Image.open(image_path)
    st.image(image, caption=os.path.basename(image_path), use_column_width=True)


# 업로드된 파일을 처리하는 큐
upload_queue = Queue()


# 폴더 선택 위젯
uploaded_files = st.file_uploader("이미지가 포함된 폴더를 업로드하세요", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        upload_queue.put(uploaded_file)

while not upload_queue.empty():
    uploaded_file = upload_queue.get()
    image = Image.open(uploaded_file)
    encoded_image = image_to_base64(image)

    # API 요청 본문 생성
    api_url = f"https://dev.digitalworker.co.kr:8743/domain-document/?domainId={domainId}&templateId={templateId}&ocrType=EDEN&angle=0"
    payload = {
        "version": "v4",
        "requestId": "string",
        "modelType": "UNIVERSAL",
        "timestamp": int(time.time()),
        "images": [
            {
                "format": image.format.lower(),
                "data": encoded_image,
                "name": uploaded_file.name
            }
        ],
        "details": "inference=cls"
    }

    # API 요청 보내기
    response = requests.post(api_url, json=payload)
    response_data = response.json()
    print(response_data)

    # 응답 표시
    if response.status_code == 200:
        if 'result' in response_data:
            if len(response_data['result']) == 0:
                st.write('result가 추출되지 않았습니다.')
            else:
                result = response_data['result'][0]["classificationResult"]
                print(response_data['result'])
                
                if isinstance(result, dict) and len(result) > 0:
                    target_element = result['templateName']
                    if isinstance(target_element, str) and len(target_element) > 0:
                        target_element = target_element.replace(" ", "_")
                        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                        documents_path = os.path.join(documents_dir, saved_dir, target_element)
                        if '신탁계약서' in target_element:
                            contract_dir = uploaded_file.name.split(' ')[0]
                            documents_path = os.path.join(documents_path, contract_dir)
                        
                        # 디렉토리가 존재하는지 확인하고 없으면 생성
                        if not os.path.exists(documents_path):
                            os.makedirs(documents_path)
                        
                        # 저장할 파일 경로 설정
                        file_path = os.path.join(documents_path, uploaded_file.name)
                        image.save(file_path)
                        st.write(f"이미지를 {file_path}에 저장했습니다.")
                    else:
                        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                        documents_path = os.path.join(documents_dir, saved_dir, '_others')
                        if not os.path.exists(documents_path):
                            os.makedirs(documents_path)
                        file_path = os.path.join(documents_path, uploaded_file.name)
                        image.save(file_path)
                        st.write(f"이미지를 {file_path}에 저장했습니다.")
        else:
            st.error("'result'가 추출되지 않았습니다")
    else:
        st.error(f"API 요청 중 오류 발생: {response.status_code}")
        st.json(response_data)
