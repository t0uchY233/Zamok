import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useRouter } from 'next/router';
import { ApiError } from '../api';

// Создаем контекст
const AuthContext = createContext();

/**
 * Проверяет, выполняется ли код на стороне клиента
 * @returns {boolean} true, если код выполняется в браузере
 */
const isBrowser = () => typeof window !== 'undefined';

/**
 * Провайдер контекста аутентификации
 * @param {Object} props - Свойства компонента
 * @returns {JSX.Element} Провайдер контекста
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();
  
  // Проверка аутентификации при загрузке приложения
  useEffect(() => {
    // Убедимся, что код выполняется только на клиенте
    if (!isBrowser()) return;
    
    async function loadUserFromToken() {
      try {
        // Проверяем, инициализирован ли authAPI
        if (apiClient.auth.init()) {
          try {
            // Временно отключаем запрос к API, т.к. бэкенд еще не готов
            // const userData = await apiClient.auth.getCurrentUser();
            // setUser(userData);
            
            // Используем моковые данные пользователя для тестирования
            setUser({
              id: '1',
              name: 'Тестовый пользователь',
              email: 'test@example.com',
              role: 'user'
            });
          } catch (error) {
            console.error('Ошибка при получении данных пользователя:', error);
            // Если токен недействителен, удаляем его
            if (isBrowser()) {
              localStorage.removeItem('token');
            }
          }
        }
      } catch (error) {
        console.error('Ошибка при проверке аутентификации:', error);
        setError(
          error instanceof ApiError 
            ? error 
            : new Error('Неизвестная ошибка аутентификации')
        );
      } finally {
        setLoading(false);
      }
    }
    
    loadUserFromToken();
  }, []);
  
  /**
   * Регистрация нового пользователя
   * @param {Object} userData - Данные пользователя
   * @returns {Promise<Object>} Результат операции
   */
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.auth.register(userData);
      setUser(response.user);
      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : error.response?.data?.message || 'Ошибка при регистрации';
      
      setError(new Error(errorMessage));
      throw error;
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Вход в систему
   * @param {Object} credentials - Данные для входа
   * @returns {Promise<Object>} Результат операции
   */
  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.auth.login(credentials);
      setUser(response.user);
      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : error.response?.data?.message || 'Ошибка при входе в систему';
      
      setError(new Error(errorMessage));
      throw error;
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Выход из системы
   * @returns {Promise<boolean>} Результат операции
   */
  const logout = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await apiClient.auth.logout();
      setUser(null);
      return true;
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : error.response?.data?.message || 'Ошибка при выходе из системы';
      
      setError(new Error(errorMessage));
      throw error;
    } finally {
      setLoading(false);
    }
  };
  
  // Определяем значение контекста
  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Хук для использования контекста аутентификации
 * @returns {Object} Контекст аутентификации
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;