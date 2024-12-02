import axios from 'axios';
import { toast } from 'react-toastify';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor para añadir el token a las solicitudes
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      const message = error.response.data.detail || "Ocurrió un error inesperado.";
      // Aquí puedes usar los componentes de Warning o Sucessfully
      if (error.response.status === 200) {
        // Mostrar mensaje de éxito
        toast.success(message);
      } else {
        // Mostrar mensaje de advertencia
        toast.warn(message);
      }
    } else {
      // Error de red o de configuración
      toast.error("Error de conexión con el servidor.");
    }
    return Promise.reject(error);
  }
);

// Interceptor de respuesta para manejar errores
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response.status === 401) {
      // Redirigir o manejar la expiración del token
      localStorage.removeItem('authToken');
    }
    return Promise.reject(error);
  }
);

export default api;