import axios from 'axios';
import { toast } from 'react-toastify';

// La URL inicial se obtiene de las variables de entorno
let currentBaseURL = import.meta.env.VITE_API_URL;

// Crear instancia de axios con la URL inicial
const api = axios.create({
  baseURL: currentBaseURL,
});

// Obtener el hostname actual del navegador
const currentHost = window.location.hostname; // devuelve la IP o dominio actual
const WEBSOCKET_URL = `ws://${currentHost}:8000/ws`; // Conectar al WebSocket del servidor FastAPI
console.log('Conectando al WebSocket en:', WEBSOCKET_URL);

// Conexión al WebSocket para recibir actualizaciones de IP y puerto
const socket = new WebSocket(WEBSOCKET_URL);

socket.addEventListener('open', () => {
  console.log(`Conectado al WebSocket en ${WEBSOCKET_URL}`);
});

socket.addEventListener('message', (event) => {
  console.log('Mensaje recibido del WebSocket:', event.data);

  // Se asume que el mensaje tiene el formato "192.168.1.10:6000"
  const [newIP, newPort] = event.data.split('<<DELIM>>');

  if (newIP && newPort) {
    const newBaseURL = `http://localhost:${newPort}`;
    if (currentBaseURL !== newBaseURL) {
      console.log(`Actualizando baseURL de ${currentBaseURL} a ${newBaseURL}`);
      currentBaseURL = newBaseURL;
      api.defaults.baseURL = newBaseURL;
    }
  } else {
    console.error('Mensaje del WebSocket en formato incorrecto:', event.data);
  }
});

// Interceptor para actualizar la baseURL y añadir el token antes de cada petición
api.interceptors.request.use(
  (config) => {
    // Se actualiza la baseURL con el valor más reciente recibido vía WebSocket
    config.baseURL = currentBaseURL;
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Interceptor para manejar respuestas y mostrar notificaciones
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!originalRequest._retry) {
      originalRequest._retry = 0;
    }

    if (originalRequest._retry < 3) {
      originalRequest._retry += 1;
      console.log(`Reintentando petición... Intento ${originalRequest._retry}`);

      // Esperar a recibir un nuevo mensaje del WebSocket para actualizar la baseURL
      const newBaseURL: string = await new Promise((resolve) => {
        const handleMessage = (event: MessageEvent) => {
          const [newIP, newPort] = event.data.split('<<DELIM>>');
          if (newIP && newPort) {
            const newBaseURL = `http://localhost:${newPort}`;
            resolve(newBaseURL);
          }
        };
        socket.addEventListener('message', handleMessage, { once: true });
      });

      currentBaseURL = newBaseURL;
      api.defaults.baseURL = newBaseURL;
      originalRequest.baseURL = newBaseURL;

      return api(originalRequest);
    }

    if (error.response) {
      const message =
        error.response.data.detail || 'Ocurrió un error inesperado.';
      if (error.response.status === 200) {
        toast.success(message);
      } else {
        toast.warn(message);
      }
      if (error.response.status === 401) {
        localStorage.removeItem('authToken');
      }
    } else {
      toast.error('Error de conexión con el servidor.');
    }
    return Promise.reject(error);
  },
);

export default api;
