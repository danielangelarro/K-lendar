import { useState, useEffect } from 'react';

import Breadcrumb from '../components/Breadcrumbs/Breadcrumb';
// import ChartOne from '../components/Charts/ChartOne';
// import ChartThree from '../components/Charts/ChartThree';
// import ChartTwo from '../components/Charts/ChartTwo';
import TableThree from '../components/Tables/TableThree';
import Sucessfully from '../components/Alerts/Sucessfully';
import TaskForm from '../components/Forms/TaskForm';
import { Task } from '../types/task';
// import { isCollitionDateRanges, Range } from './Calendar';

const taskData: Task[] = [
  {
    id: 0,
    title: 'Free package',
    description: '0000000000000000000000000000000000000000000000000000000000000000000000000000',
    start_time: new Date(2024,10,7),
    end_time: new Date(2024,11,7),
    group: `Jan 13,2023`,
    status: 'confirmed',
    event_type: 'group',
  },
  {
    id: 1,
    title: 'Standard Package',
    description: '1111111111111111111111111111111111111111111111111111111111111111111111111111',
    start_time: new Date(2024,10,27),
    end_time: new Date(2024,11,4),
    group: ``,
    status: 'confirmed',
    event_type: 'personal',
  },
  {
    id: 2,
    title: 'Business Package',
    description: '2222222222222222222222222222222222222222222222222222222222222222222222222222222',
    start_time: new Date(2024,10,6),
    end_time: new Date(2024,11,6),
    group: `Jan 13,2023`,
    status: 'cancelled',
    event_type: 'group',
  },
  {
    id: 3,
    title: 'Standard Package',
    description: '33333333333333333333333333333333333333333333333333333333333333333333333333333333',
    start_time: new Date(2024,10,9),
    end_time: new Date(2024,11,11),
    group: `Jan 13,2023`,
    status: 'pending',
    event_type: 'group',
  },
];

const TaskPage = () => {
  const [ tasks, setTasks ] = useState<Task[]>(taskData)
  const [ modalSuccessfully, setModalSuccessfully ] = useState<boolean>(false)
  const [ msgSuccessfully, setMsgSuccessfully ] = useState<string>('')
  const [ selectedTask, setSelectedTask ] = useState<Task | undefined>(undefined)
  const [ modalEditTask, setModalEditTask ] = useState<boolean>(false)
  
  useEffect(() => {
    if (modalSuccessfully) setTimeout(() => setModalSuccessfully(false), 1500);
  }, [modalSuccessfully]);

  function del(id: number) {
    console.log('hacer peticion')
    const new_tasks = tasks.filter(tarea => tarea.id != id)
    setTasks(new_tasks)

    const resp = {"detail": "Event deleted successfully"}
    setMsgSuccessfully(resp["detail"])
    setModalSuccessfully(true)
  }

  function start_edit(id: number) {
    console.log('hacer peticion')
    const task = tasks.filter(tarea => tarea.id == id)[0]
    setSelectedTask(task)

    setModalEditTask(true)
  }

  function end_edit(task: Task) {
    console.log('hacer peticion')

    if (task.id >= 0) {
      const old_task = tasks.filter(tarea => tarea.id == task.id)[0]
      old_task.title = task.title
      old_task.description = task.description
      old_task.start_time = task.start_time
      old_task.end_time = task.end_time
      old_task.group = task.group
      old_task.status = task.status
      old_task.event_type = task.event_type
    }

    else {
      tasks.push({
        id: tasks.length,
        title: task.title,
        description: task.description,
        start_time: task.start_time,
        end_time: task.end_time,
        group: task.group,
        status: task.status,
        event_type: task.event_type,
      })
    }

    setModalEditTask(false)
  }

  // function filtrar(range: Range) {
  //   setTasks(tasks.filter(task => 
  //     isCollitionDateRanges({
  //       start_time: task.start_time,
  //       end_time: task.end_time,
  //     }, range)
  //   ))
  // }

  function clickCreate() {
    setSelectedTask(undefined)
    setModalEditTask(true)
  }

  return (
    <>
      { modalSuccessfully && (
        <div className=''>
          <Sucessfully msg={msgSuccessfully}/>
        </div>
      )}
      <Breadcrumb pageName="Task" />
      
      { modalEditTask && (
        <div className=''>
          <TaskForm edit={end_edit} set={setModalEditTask} old_task={selectedTask} header={selectedTask ? 'Edit Task' : 'Create Task'}/>
        </div>
      )}

      {!modalEditTask && (
        <div className="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">
          <div className="col-span-12 xl:col-span-8">
            <TableThree del={del} tasks={tasks} edit={start_edit}/>{/* filtrar={filtrar} */}
            <button onClick={() => clickCreate()} className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90">
              New Task
            </button>
          </div>
          {/* <ChartOne />
          <ChartTwo />
          <ChartThree /> */}
        </div>
      )}
    </>
  );
};

export default TaskPage;
