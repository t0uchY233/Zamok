from flask import jsonify, request, current_app
from app import app
from app.database import User, Owner
from datetime import datetime, timedelta
import os
import jwt
import functools
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

# Декоратор для защиты маршрутов
def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Получаем токен из заголовка
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing'
            }), 401
            
        try:
            # Декодируем токен
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
            
            # Получаем пользователя по Telegram ID
            current_user = User.query.filter_by(telegram_id=data['telegram_id']).first()
            if not current_user:
                # Проверяем, может это владелец
                current_user = Owner.query.filter_by(telegram_id=data['telegram_id']).first()
                if not current_user:
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid token'
                    }), 401
                    
        except jwt.ExpiredSignatureError:
            return jsonify({
                'status': 'error',
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token'
            }), 401
            
        # Передаем пользователя в функцию
        return f(current_user, *args, **kwargs)
        
    return decorated

def upload_to_drive(file_data, filename):
    """Загрузка файла в Google Drive"""
    try:
        credentials_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.getenv('GOOGLE_CREDENTIALS_FILE') + '.json')
        
        if not os.path.exists(credentials_file):
            app.logger.error(f"Файл учетных данных не найден: {credentials_file}")
            raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
            
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
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
        
        # Устанавливаем публичный доступ
        service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        
        return f"https://drive.google.com/uc?id={file.get('id')}"
        
    except Exception as e:
        app.logger.error(f"Ошибка при загрузке в Google Drive: {str(e)}")
        raise

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Аутентификация пользователя и выдача JWT токена"""
    try:
        data = request.json
        
        if not data or 'telegram_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing telegram_id'
            }), 400
            
        telegram_id = data['telegram_id']
        
        # Проверяем, существует ли пользователь
        user = User.query.filter_by(telegram_id=telegram_id).first()
        
        # Если пользователя нет - проверяем, может это владелец
        if not user:
            owner = Owner.query.filter_by(telegram_id=telegram_id).first()
            if not owner:
                return jsonify({
                    'status': 'error',
                    'message': 'User not found. Please register first.'
                }), 404
                
            # Выдаем токен для владельца
            token = jwt.encode({
                'telegram_id': owner.telegram_id,
                'is_owner': True,
                'exp': datetime.utcnow() + timedelta(days=7)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")
            
            return jsonify({
                'status': 'success',
                'token': token,
                'user_type': 'owner',
                'user_id': owner.id,
                'is_verified': owner.is_verified
            })
        
        # Выдаем токен для обычного пользователя
        token = jwt.encode({
            'telegram_id': user.telegram_id,
            'is_owner': False,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'status': 'success',
            'token': token,
            'user_type': 'user',
            'user_id': user.id,
            'is_verified': user.is_verified
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка при входе: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Регистрация нового пользователя"""
    try:
        if 'document_photo' not in request.files:
            return jsonify({'status': 'error', 'message': 'No document photo provided'}), 400
            
        data = request.form
        photo = request.files['document_photo']
        
        if 'telegram_id' not in data:
            return jsonify({'status': 'error', 'message': 'Missing telegram_id'}), 400
        
        # Проверяем существование пользователя
        existing_user = User.query.filter_by(telegram_id=data['telegram_id']).first()
        if existing_user:
            return jsonify({'status': 'error', 'message': 'User already exists'}), 400
        
        # Загружаем фото в Google Drive
        photo_url = upload_to_drive(photo.read(), f"document_{data['telegram_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        
        # Создаем нового пользователя
        user = User(
            telegram_id=int(data['telegram_id']),
            username=data.get('username'),
            full_name=data.get('full_name')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Генерируем токен
        token = jwt.encode({
            'telegram_id': user.telegram_id,
            'is_owner': False,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'status': 'success',
            'user_id': user.id,
            'token': token,
            'message': 'Registration successful, waiting for verification'
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка при регистрации: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/auth/verify/<int:user_id>', methods=['POST'])
@token_required
def verify_user(current_user, user_id):
    """Ручная верификация пользователя администратором"""
    try:
        # Проверяем, является ли текущий пользователь владельцем с правами админа
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return jsonify({
                'status': 'error', 
                'message': 'Insufficient permissions'
            }), 403
        
        user = User.query.get_or_404(user_id)
        
        data = request.json
        if not data or 'verified' not in data:
            return jsonify({
                'status': 'error', 
                'message': 'Missing verification status'
            }), 400
            
        if data.get('verified'):
            user.is_verified = True
            db.session.commit()
            return jsonify({
                'status': 'success', 
                'message': 'User verified successfully'
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'Verification rejected'
            }), 400
            
    except Exception as e:
        app.logger.error(f"Ошибка при верификации: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/auth/status/<int:telegram_id>', methods=['GET'])
def check_auth_status(telegram_id):
    """Проверка статуса верификации пользователя"""
    try:
        user = User.query.filter_by(telegram_id=telegram_id).first()
        
        if not user:
            # Проверяем, может это владелец
            owner = Owner.query.filter_by(telegram_id=telegram_id).first()
            if not owner:
                return jsonify({
                    'status': 'error', 
                    'message': 'User not found'
                }), 404
                
            return jsonify({
                'status': 'success',
                'user_type': 'owner',
                'user_id': owner.id,
                'is_verified': owner.is_verified,
                'registration_date': owner.registration_date.isoformat() if owner.registration_date else None
            })
            
        return jsonify({
            'status': 'success',
            'user_type': 'user',
            'user_id': user.id,
            'is_verified': user.is_verified,
            'registration_date': user.registration_date.isoformat() if user.registration_date else None
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка при проверке статуса: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Server error: {str(e)}'
        }), 500 