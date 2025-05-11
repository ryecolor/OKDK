import axios from 'axios';

const API_URL = 'http://i12a204.p.ssafy.io:8000/api/';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// 요청 인터셉터 
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwtToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 403 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axiosInstance.post('token/refresh/', { refresh: refreshToken });
        const { access } = response.data;
        localStorage.setItem('jwtToken', access);
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const register = (username, password, district) => {
  return axiosInstance.post('register/', { username, password, district });
};


export const login = async (username, password) => {
  try {
    const response = await axiosInstance.post('token/', { username, password });
    const { access, refresh } = response.data;
    localStorage.setItem('jwtToken', access);
    localStorage.setItem('refreshToken', refresh);
    setAuthToken(access);
    return response;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('jwtToken');
  localStorage.removeItem('refreshToken');
  delete axiosInstance.defaults.headers.common['Authorization'];
};

export const getCurrentUser = () => {
  return JSON.parse(localStorage.getItem('user'));
};

export const deleteAccount = async (password) => {
  try {
    const response = await axiosInstance.delete('delete/', {
      data: { password }
    });
    
    // 응답 상태 코드 확인
    if (response.status === 200) {
      return { success: true, data: response.data };
    } else {
      throw new Error('비밀번호가 올바르지 않습니다.');
    }
  } catch (error) {
    // 서버에서 반환된 에러 처리
    if (error.response) {
      if (error.response.status === 401 || error.response.status === 400) {
        throw new Error(error.response.data.error || '비밀번호가 올바르지 않습니다.');
      }
    }
    throw new Error('회원 탈퇴 처리 중 오류가 발생했습니다.');
  }
};


// 토큰을 설정하는 함수
export const setAuthToken = (token) => {
  if (token) {
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('jwtToken', token);
  } else {
    delete axiosInstance.defaults.headers.common['Authorization'];
    localStorage.removeItem('jwtToken');
  }
};
