import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumbs/Breadcrumb';
import TableThree from '../components/Tables/TableThree';
import Sucessfully from '../components/Alerts/Sucessfully';
import TaskForm from '../components/Forms/TaskForm';
import { Task } from '../types/task';
import Loader from '../common/Loader';

import api from '../api/axios'; // Asegúrate de importar tu configuración de axios
import { useAuthContext } from '../context/AuthContext'; // Importa el contexto de autenticación


const TaskPage = () => {
  const params = useParams();
  const [filterStartDate, setFilterStartDate] = useState(params.filterDate || new Date().toISOString().split('T')[0]);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [modalSuccessfully, setModalSuccessfully] = useState<boolean>(false);
  const [msgSuccessfully, setMsgSuccessfully] = useState<string>('');
  const [selectedTask, setSelectedTask] = useState<Task | undefined>(undefined);
  const [modalEditTask, setModalEditTask] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Obtén el usuario del contexto de autenticación
  const { user } = useAuthContext();

  // Cargar tareas al montar el componente
  useEffect(() => {
    fetchTasks();
  }, []);

  // Efecto para manejar el mensaje de éxito
  useEffect(() => {
    if (modalSuccessfully) setTimeout(() => setModalSuccessfully(false), 1500);
  }, [modalSuccessfully]);

  // Función para obtener tareas
  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/events');
      setTasks(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error al obtener tareas:', error);
      setIsLoading(false);
    }
  };

  // Eliminar tarea
  const del = async (id: string) => {
    try {
      await api.delete(`/events/${id}`);
      
      // Actualizar estado local
      const new_tasks = tasks.filter(tarea => tarea.id !== id);
      setTasks(new_tasks);

      // Mostrar mensaje de éxito
      setMsgSuccessfully("Tarea eliminada exitosamente");
      setModalSuccessfully(true);
    } catch (error) {
      console.error('Error al eliminar tarea:', error);
      setMsgSuccessfully("Error al eliminar tarea");
      setModalSuccessfully(true);
    }
  };

  // Iniciar edición de tarea
  const start_edit = (id: string) => {
    const task = tasks.find(tarea => tarea.id === id);
    setSelectedTask(task);
    setModalEditTask(true);
  };

  // Finalizar edición/creación de tarea
  const end_edit = async (task: Task) => {
    try {
      if (task.id) {
        // Editar tarea existente
        const response = await api.put(`/events/${task.id}`, task);
        
        // Actualizar estado local
        setTasks(tasks.map(t => t.id === task.id ? response.data : t));
        
        setMsgSuccessfully("Tarea actualizada exitosamente");
      } else {
        // Crear nueva tarea
        const response = await api.post('/events/create/', task);
        
        // Agregar tarea al estado local
        setTasks([...tasks, response.data]);
        
        setMsgSuccessfully("Tarea creada exitosamente");
      }

      // Cerrar modal y mostrar mensaje
      setModalEditTask(false);
      setModalSuccessfully(true);
    } catch (error) {
      console.error('Error al guardar tarea:', error);
      setMsgSuccessfully("Error al guardar tarea");
      setModalSuccessfully(true);
    }
  };

  // Abrir modal para crear nueva tarea
  const clickCreate = () => {
    setSelectedTask(undefined);
    setModalEditTask(true);
  };

  const filtrar = async (start_datetime: Date, end_datetime: Date) => {
    try {
      // Pedir las tareas en ese rango
      setIsLoading(true);
      const response = await api.get(`/agendas/${start_datetime.toISOString()}/${end_datetime.toISOString()}`);
      
      // Actualizar estado local
      setTasks(response.data.events); 
      setIsLoading(false);
    
    } catch (error) {
      console.error('Error filtrar tareas:', error);
      setMsgSuccessfully("Error to filter tasks.");
      setModalSuccessfully(true);
      setIsLoading(false);
    }
  };

  // Renderizado condicional con estado de carga
  if (isLoading) {
    return <Loader />;
  }

  return (
    <>
      {modalSuccessfully && (
        <div className=''>
          <Sucessfully msg={msgSuccessfully}/>
        </div>
      )}

      <Breadcrumb pageName="Task" />

      {modalEditTask && (
        <div className=''>
          <TaskForm 
            set={setModalEditTask}
            edit={end_edit} 
            old_task={selectedTask}
            header={selectedTask ? 'Edit Task' : 'Create Task'}
          />
        </div>
      )}

      {!modalEditTask && (
        <div className="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">
          <div className="col-span-12 xl:col-span-8">
            <TableThree 
              filtrar={filtrar}
              del={del} 
              tasks={tasks} 
              edit={start_edit}
              filterStartDate={filterStartDate}
            />
            <button 
              onClick={clickCreate} 
              className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90"
            >
              New Task
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default TaskPage;