import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter

import os
from pdf2image import convert_from_path

def split_pdf_to_images(pdf_path, output_dir):
    # Documents 폴더 경로
    documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
    # output_dir에 Documents 폴더 경로를 추가
    output_path = os.path.join(documents_folder, output_dir)

    # 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # PDF 파일을 이미지로 변환
    images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        output_filename = f'{output_path}/page_{i + 1}.png'
        image.save(output_filename, 'PNG')

    print(f'PDF 파일이 페이지별로 이미지로 변환되어 {output_path}에 저장되었습니다.')

# 사용 예시
pdf_path = 'BL.pdf'  # 분할할 PDF 파일 경로
output_dir = 'Split_PDF_Pages'     # 저장할 디렉토리 이름

split_pdf_to_images(pdf_path, output_dir)



