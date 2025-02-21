from flask import jsonify, request
from app import app, db
from app.database import User
from datetime import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

def upload_to_drive(file_data, filename):
    """Загрузка файла в Google Drive"""
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_CREDENTIALS_FILE'),
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    
    service = build('drive', 'v3', credentials=credentials)
    
    # Создаем файл в памяти
    fh = BytesIO(file_data)
    
    # Метаданные файла
    file_metadata = {'name': filename}
    
    # Загружаем файл
    media = MediaIoBaseUpload(fh, mimetype='image/jpeg', resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return f"https://drive.google.com/file/d/{file.get('id')}/view"

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    if 'document_photo' not in request.files:
        return jsonify({'status': 'error', 'message': 'No document photo provided'}), 400
        
    data = request.form
    photo = request.files['document_photo']
    
    # Проверяем существование пользователя
    existing_user = User.query.filter_by(telegram_id=data['telegram_id']).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400
    
    try:
        # Загружаем фото в Google Drive
        photo_url = upload_to_drive(photo.read(), f"document_{data['telegram_id']}.jpg")
        
        # Создаем нового пользователя
        user = User(
            telegram_id=data['telegram_id'],
            username=data.get('username'),
            full_name=data.get('full_name'),
            document_photo_url=photo_url
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'user_id': user.id,
            'message': 'Registration successful, waiting for verification'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/verify/<int:user_id>', methods=['POST'])
def verify_user(user_id):
    """Ручная верификация пользователя администратором"""
    user = User.query.get_or_404(user_id)
    
    data = request.json
    if data.get('verified'):
        user.is_verified = True
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'User verified successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Verification rejected'}), 400

@app.route('/api/auth/status/<int:telegram_id>', methods=['GET'])
def check_auth_status(telegram_id):
    """Проверка статуса верификации пользователя"""
    user = User.query.filter_by(telegram_id=telegram_id).first()
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
    return jsonify({
        'status': 'success',
        'is_verified': user.is_verified,
        'registration_date': user.created_at.isoformat()
    }) 