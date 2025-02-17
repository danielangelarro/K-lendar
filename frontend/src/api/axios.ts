import axios from 'axios';
import { toast } from 'react-toastify';

const servers = [
  import.meta.env.VITE_API_URL1,
  import.meta.env.VITE_API_URL2,
  import.meta.env.VITE_API_URL3,
];

const pingServer = (serverUrl: string): Promise<string> => {
  return axios
    .get(`${serverUrl}/ping`, { timeout: 3000 }) // timeout de 3 segundos
    .then(() => serverUrl);
};

export const selectServer = async (): Promise<string> => {
  const pingPromises = servers.map((url) => pingServer(url));
  try {
    const selectedServer = await Promise.any(pingPromises);
    return selectedServer;
  } catch (error) {
    throw new Error("No se pudo conectar a ningún servidor disponible.");
  }
};

const api = axios.create();

export const initApi = async (): Promise<void> => {
  try {
    const selectedServer = await selectServer();
    api.defaults.baseURL = selectedServer;
    console.log(`Servidor seleccionado: ${selectedServer}`);
  } catch (error) {
    toast.error("No se pudo conectar a ningún servidor disponible.");
    throw error;
  }
};

// Interceptor para añadir el token a las solicitudes
api.interceptors.request.use(
  async (config) => {
    await initApi();

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