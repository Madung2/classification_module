import streamlit as st
from PIL import Image
from encoding import image_to_base64
import requests
from dotenv import load_dotenv
import json
import time
import os
import io

load_dotenv()
domainId = os.getenv('domainId')
templateId = os.getenv('templateId')
saved_dir = os.getenv('saved_dir')

# 페이지 제목
st.title("이미지 분류 모듈")

# 폴더 선택 위젯
uploaded_files = st.file_uploader("이미지가 포함된 폴더를 업로드하세요", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # PIL을 사용하여 이미지를 열기
        image = Image.open(uploaded_file)
        encoded_image = image_to_base64(image)
        
        # 이미지 표시
        #st.image(image, caption=f"업로드한 이미지: {uploaded_file.name}", use_column_width=True)
        
        # 이미지 정보 표시
        #st.write(f"이미지 파일 이름: {uploaded_file.name}")
        #st.write(f"이미지 크기: {image.size}")
        #st.write(f"이미지 포맷: {image.format}")
        
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

        # 응답 표시
        if response.status_code == 200:
            st.success("API 요청이 성공적으로 전송되었습니다.")
            if 'result' in response_data:
                print(response_data,'response_data')
                if len(response_data['result']) == 0:
                    st.write('result가 추출되지 않았습니다.')
                else:
                    result = response_data['result'][0]["classificationResult"]
                    if isinstance(result, dict) and len(result) > 0:
                        target_element = result['templateName']
                        if isinstance(target_element, str) and len(target_element) > 0:
                            target_element = target_element.replace(" ", "_")
                            documents_path = os.path.join(os.path.expanduser("~"), saved_dir, target_element)
                            
                            # 디렉토리가 존재하는지 확인하고 없으면 생성
                            if not os.path.exists(documents_path):
                                os.makedirs(documents_path)
                                st.write(f"{documents_path} 디렉토리를 생성했습니다.")
                            else:
                                st.write(f"{documents_path} 디렉토리가 이미 존재합니다.")
                            
                            # 저장할 파일 경로 설정
                            file_path = os.path.join(documents_path, uploaded_file.name)
                            image.save(file_path)
                            st.write(f"이미지를 {file_path}에 저장했습니다.")
            else:
                st.error("'result'가 추출되지 않았습니다")
        else:
            st.error(f"API 요청 중 오류 발생: {response.status_code}")
            st.json(response_data)